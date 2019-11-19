import json
import pandas as pd
from pandas.io.json import json_normalize
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn import metrics


class Hackthon():
    def __init__(self):
        ##JSON paths
        PATH_PREV_HEATS = 'data/1/previous_heats_with_properties.json'
        PATH_CONSTRAINS = 'data/1/constraints.json'
        PATH_PROD_SCHED = 'data/1/production_schedule.json'
        PATH_SCRAP_INV = 'data/1/scrap_inventory.json'
        PATH_SCRAP_ORD = 'data/1/scrap_orders.json'

        prev_heats = self.loadjsons(PATH_PREV_HEATS)
        constriants = self.loadjsons(PATH_CONSTRAINS, **{'table_name': "scrap_type_constraints_per_heat"})
        prod_sched = self.loadjsons(PATH_PROD_SCHED)
        scrap_inv = self.loadjsons(PATH_SCRAP_INV)
        scrap_ord = self.loadjsons(PATH_SCRAP_ORD)

        scrap_prices = scrap_ord.groupby('scrap_type')['price_per_ton'].mean()
        X = prev_heats[['actual_recipe.bushling', 'actual_recipe.pig_iron', 'actual_recipe.municipal_shred',
                        'actual_recipe.skulls']].values
        y = prev_heats.loc[:, ['chemistry.cu_pct']].values

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

        regressor = LinearRegression()
        regressor.fit(X_train, y_train)

        # To retrieve the intercept:
        print(regressor.intercept_)
        # For retrieving the slope:
        print(regressor.coef_)

    @staticmethod
    def loadjsons(jsonpath, **kwargs):
        if 'table_name' in kwargs:
            with open(jsonpath) as prev_heats:
                prev_heats = json.load(prev_heats)
            prev_heats = json_normalize(data = prev_heats[kwargs["table_name"]])
        else:
            with open(jsonpath) as prev_heats:
                prev_heats = json.load(prev_heats)
            prev_heats = json_normalize(data = prev_heats)
        return prev_heats



if __name__ == "__main__":
    ht=Hackthon()
    print('')