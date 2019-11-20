#all needed imports
import sys
import json
import pandas as pd
import numpy as np
from pandas.io.json import json_normalize

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn import metrics

from scipy.optimize import curve_fit
import scipy

from pulp import *


class Hackthon():
    def __init__(self,n):
        ##JSON paths
        PATH_PREV_HEATS = f'data/{n}/previous_heats_with_properties.json'
        PATH_CONSTRAINS = f'data/{n}/constraints.json'
        PATH_PROD_SCHED = f'data/{n}/production_schedule.json'
        PATH_SCRAP_INV = f'data/{n}/scrap_inventory.json'
        PATH_SCRAP_ORD = f'data/{n}/scrap_orders.json'

        # load all jsons
        prev_heats = self.loadjsons(PATH_PREV_HEATS)
        constriants = self.loadjsons(PATH_CONSTRAINS, **{'table_name': "scrap_type_constraints_per_heat"})
        prod_sched = self.loadjsons(PATH_PROD_SCHED)
        scrap_inv = self.loadjsons(PATH_SCRAP_INV)
        scrap_ord = self.loadjsons(PATH_SCRAP_ORD)

        # inventory
        bushlings_inventory = scrap_inv.loc[scrap_inv['scrap_type'] == 'bushling', 'weight'].values[0]
        pig_iron_inventory = scrap_inv.loc[scrap_inv['scrap_type'] == 'pig_iron', 'weight'].values[0]
        municipal_shred_inventory = scrap_inv.loc[scrap_inv['scrap_type'] == 'municipal_shred', 'weight'].values[0]
        skulls_inventory = scrap_inv.loc[scrap_inv['scrap_type'] == 'skulls', 'weight'].values[0]

        #--------------------------------------------------------------------------------------------------------------
        ''' multiple_linear_regress_sklearn 
        X_prev_heats = prev_heats[['actual_recipe.bushling', 'actual_recipe.municipal_shred',
                        'actual_recipe.skulls']].values
        y_prev_heats = prev_heats.loc[:, ['chemistry.cu_pct']].values
        [y_pred_prev_heats, y_test_prev_heats]=self.multiple_linear_regress_sklearn(X_prev_heats,y_prev_heats)
        print('predictied cu')
        print(y_pred_prev_heats)
        print('testdata: ')
        print(y_test_prev_heats)'''
        #--------------------------------------------------------------------------------------------------------------
        '''multiple_linear_regress_scipy'''

        # get input X and output y values for mutli linear regression model - yield
        X_yield = np.squeeze(np.transpose(prev_heats[['actual_recipe.bushling', 'actual_recipe.pig_iron',
                                                    'actual_recipe.municipal_shred', 'actual_recipe.skulls']].values))
        y_yield = np.squeeze(np.transpose(prev_heats.loc[:, ['tap_weight']].values))

        [popt_yield, pcov_yield, p_sigma_yield] = self.multiple_linear_regress_scipy_yld(X_yield, y_yield)

        # get input X and output y values for mutli linear regression model - cu
        X_cu = np.squeeze(np.transpose(
            prev_heats[['actual_recipe.bushling', 'actual_recipe.pig_iron', 'actual_recipe.municipal_shred', 'actual_recipe.skulls']].values))
        y_cu = np.squeeze(np.transpose(prev_heats.loc[:, ['chemistry.cu_pct']].values*prev_heats.loc[:, ['tap_weight']].values))

        [popt_cu, pcov_cu, p_sigma_cu]=self.multiple_linear_regress_scipy_cu(X_cu, y_cu, popt_yield)


        #--------------------------------------------------------------------------------------------------------------
        # delta for weights
        wgt_delta = pd.DataFrame({'required_weight': []})
        wgt_delta['required_weight'] = prev_heats['required_weight']

        wgt_delta['sum_scrap_wgt'] = prev_heats[
            ['actual_recipe.bushling', 'actual_recipe.pig_iron', 'actual_recipe.municipal_shred',
             'actual_recipe.skulls']].sum(axis=1)

        wgt_delta['delta'] = wgt_delta['sum_scrap_wgt'] - wgt_delta['required_weight']
        wgt_lower_tolerance = wgt_delta['delta'].min() if wgt_delta['delta'].min() <= 0 else 0
        wgt_upper_tolerance = wgt_delta['delta'].max()



        # self.solver(1050, wgt_upper_tolerance, wgt_lower_tolerance, 0.15, constriants, scrap_ord, popt_cu, popt_yield, bushlings_inventory, pig_iron_inventory, municipal_shred_inventory, skulls_inventory)
        prediction_heats=pd.DataFrame()
        prod_names = pd.DataFrame(columns=['heat_seq', 'heat_id', 'steel_grade', 'predicted_tap_weight', 'predicted_chemistry.cu_pct'])
        for row in prod_sched.iterrows():
            a=self.solver(row[1]['required_weight'], wgt_upper_tolerance, wgt_lower_tolerance, row[1]['chemistry.cu_pct'], constriants, scrap_ord, popt_cu,
                        popt_yield, bushlings_inventory, pig_iron_inventory, municipal_shred_inventory,
                        skulls_inventory)
            df = pd.DataFrame([a], columns=a.keys())
            pred_tap_weight=popt_yield[0]*df['bushlings_wgt'][0]+popt_yield[1]*df['pig_iron_wgt'][0]+popt_yield[2]*df['municipal_shred_wgt'][0]+popt_yield[3]*df['skulls_wgt'][0]
            cu=(popt_cu[0]*df['bushlings_wgt'][0]+popt_cu[1]*df['pig_iron_wgt'][0]+popt_cu[2]*df['municipal_shred_wgt'][0]+popt_cu[3]*df['skulls_wgt'][0])/pred_tap_weight

            prod_names.loc[0] = [row[1]['heat_seq'], row[1]['heat_id'], row[1]['steel_grade'], pred_tap_weight, cu]
            new_row=pd.concat([prod_names, df], axis=1)

            prediction_heats = pd.concat([prediction_heats, new_row])

            bushlings_inventory = bushlings_inventory - df['bushlings_wgt'][0]
            pig_iron_inventory = pig_iron_inventory - df['pig_iron_wgt'][0]
            municipal_shred_inventory = municipal_shred_inventory - df['municipal_shred_wgt'][0]
            skulls_inventory = skulls_inventory - df['skulls_wgt'][0]
            print('')

        prediction_heats.reset_index(inplace=True, drop=True)

        self.dump_data_frame_as_json(prediction_heats, f'{n}_results.json')

        #-------------------------

    def solver(self, req_weight, upper_bound, lower_bound, cu, constriants, scrap_ord, popt_cu, popt_yield, bushlings_inventory, pig_iron_inventory, municipal_shred_inventory, skulls_inventory):

        cu_bushling = popt_cu[0]
        cu_pig_iron = popt_cu[1]
        cu_municipal_shred = popt_cu[2]
        cu_skulls = popt_cu[3]

        yield_bushling = popt_yield[0]
        yield_pig_iron = popt_yield[1]
        yield_municipal_shred = popt_yield[2]
        yield_skulls = popt_yield[3]

        # calculate scrap prices per mean
        scrap_prices = scrap_ord.groupby('scrap_type')['price_per_ton'].mean()

        tap_weight_upper_bound = req_weight + upper_bound
        tap_weight_lower_bound = req_weight + lower_bound

        prob = LpProblem("Cost of Scrap in Steel Grade Recipes", LpMinimize)

        [min_pig_iron, max_pig_iron]=self.constriants_per_type('pig_iron', constriants)
        [min_municipal_shred, max_municipal_shred] = self.constriants_per_type('municipal_shred', constriants)
        [min_bushling, max_bushling] = self.constriants_per_type('bushlings', constriants)


        # Create problem variables
        bushlings_wgt = LpVariable("bushlings_wgt", lowBound=min_bushling, upBound=max_bushling, cat='Continuous')
        pig_iron_wgt = LpVariable("pig_iron_wgt", lowBound=min_pig_iron, upBound=max_pig_iron, cat='Continuous')
        municipal_shred_wgt = LpVariable("municipal_shred_wgt", lowBound=min_municipal_shred, upBound=max_municipal_shred, cat='Continuous')
        skulls_wgt = LpVariable("skulls_wgt", lowBound=0, upBound=None, cat='Continuous')

        # The objective function is added to 'prob' first
        prob += scrap_prices.bushling * bushlings_wgt + scrap_prices.pig_iron * pig_iron_wgt + scrap_prices.municipal_shred * municipal_shred_wgt + scrap_prices.skulls * skulls_wgt, "cost; to be minimized"

        # The constraints are entered
        prob += bushlings_wgt + pig_iron_wgt + municipal_shred_wgt + skulls_wgt >= tap_weight_lower_bound, "lower bound of required weight"
        prob += bushlings_wgt + pig_iron_wgt + municipal_shred_wgt + skulls_wgt <= tap_weight_upper_bound, "upper bound of required weight"

        # prob += bushlings_wgt + pig_iron_wgt + municipal_shred_wgt + skulls_wgt == 1050, "upper bound of required weight"

        prob += yield_bushling * cu_bushling * bushlings_wgt + yield_pig_iron * cu_pig_iron * pig_iron_wgt + yield_municipal_shred * cu_municipal_shred * municipal_shred_wgt + yield_skulls * cu_skulls * skulls_wgt <= (
                    yield_bushling * bushlings_wgt + yield_pig_iron * pig_iron_wgt + yield_municipal_shred * municipal_shred_wgt + yield_skulls * skulls_wgt) * cu, "Cu constraint"
        prob += bushlings_inventory - bushlings_wgt >= 0, "bushlings inventory constraint"
        prob += pig_iron_inventory - pig_iron_wgt >= 0, "pig_iron inventory constraint"
        prob += municipal_shred_inventory - municipal_shred_wgt >= 0, "municipal_shred inventory constraint"
        prob += skulls_inventory - skulls_wgt >= 0, "skulls inventory constraint"

        # The problem data is written to an .lp file
        prob.writeLP("Scrap_recipes.lp")

        # The problem is solved using PuLP's choice of Solve
        prob.solve()

        result={}
        for v in prob.variables():
            print(v.name, "=", v.varValue)
            result.update( {v.name : v.varValue} )

        return result


    @staticmethod
    def constriants_per_type(type, constriants):
        try:
            constriants_type = constriants.loc[constriants['scrap_type'] == type]
            try:
                min = constriants_type.loc[constriants_type['type'] == 'minimum', 'weight'].values[0]
            except:
                min = 0
            try:
                max = constriants_type.loc[constriants_type['type'] == 'maximum', 'weight'].values[0]
            except:
                max = None
        except:
            min = 0
            max = None

        return min, max

    @staticmethod
    def multiple_linear_regress_scipy_cu(X, y, yld):

        def fn(x, b, c, d, e):
            return yld[0]*b * x[0] + yld[1]*c * x[1] + yld[2]*d * x[2] + yld[3]*e * x[3]

        # covaraince = average distance from regression line?
        popt, pcov = curve_fit(fn, X, y, bounds=(0, 1))
        print('popt cu')
        print(popt)
        print('pcov cu')
        print(pcov)

        # standard deviation errors
        p_sigma = np.sqrt(np.diag(pcov))
        print(p_sigma)

        return popt, pcov, p_sigma

    @staticmethod
    def multiple_linear_regress_scipy_yld(X, y):

        def fn(x, b, c, d, e):
            return b * x[0] + c * x[1] + d * x[2] + e * x[3]

        # covaraince = average distance from regression line?
        popt, pcov = curve_fit(fn, X, y, bounds=(0, 1))
        print('popt yld')
        print(popt)
        print('pcov yld')
        print(pcov)

        # standard deviation errors
        p_sigma = np.sqrt(np.diag(pcov))
        print(p_sigma)

        return popt, pcov, p_sigma

    @staticmethod
    def multiple_linear_regress_sklearn(X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

        regressor = LinearRegression()

        regressor.fit(X_train, y_train)

        # To retrieve the intercept:
        print(regressor.intercept_)
        # For retrieving the slope:
        print('coef')
        print(regressor.coef_)

        y_pred = regressor.predict(X_test)

        return y_pred, y_test

    @staticmethod
    def loadjsons(jsonpath, **kwargs):
        if 'table_name' in kwargs:
            with open(jsonpath) as data:
                data = json.load(data)
            data = json_normalize(data = data[kwargs["table_name"]])
        else:
            with open(jsonpath) as data:
                data = json.load(data)
            data = json_normalize(data = data)

        return data

    @staticmethod
    def dump_data_frame_as_json(df, name):
        """Dumps a dataframe as json under name n,
        make sure every row has its own line in the result file
        """
        with open(name + "_ temp", 'w') as outfile:
            json.dump(df.to_dict(orient='record'), outfile)
        with open(name + "_ temp", 'r') as outfile:
            f = outfile.read().replace("},", "},\n")
        with open(name, 'w') as outfile:
            outfile.write(f)
        os.remove(name + "_ temp")

if __name__ == "__main__":
    Hackthon(sys.argv[1])