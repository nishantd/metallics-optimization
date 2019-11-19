import pandas as pd
import json
import pickle

commodities = ['bushling', 'pig_iron', 'municipal_shred', 'skulls']

def calculate_scrap_cost(scrap_orders):
    """
    calculate_scrap_cost: Calculate the average cost of scrap from the orders
    
    inputs:
        scrap_orders - location of scrap orders json
    outputs:
        scrap_cost - dictionary of scrap_type:scrap_cost
    """
    with open(scrap_orders) as json_file:
        scrap_orders = json.load(json_file)
    scrap_orders = pd.DataFrame(scrap_orders)
    scrap_orders['total_cost'] = scrap_orders['price_per_ton'] * scrap_orders['weight']
    scrap_orders_grouped = scrap_orders.groupby('scrap_type').sum().reset_index()
    scrap_orders_grouped['avg_price_per_ton'] = scrap_orders_grouped['total_cost']/scrap_orders_grouped['weight']
    scrap_cost = dict(zip(scrap_orders_grouped.scrap_type, scrap_orders_grouped.avg_price_per_ton))
    return scrap_cost

ddef value_in_use(commodity_inputs, yield_model, copper_model, copper_target, scrap_cost):
    """
    value_in_use: calculate the value in use for a given set of commodity inputs
    
    inputs: 
        commodity_inputs - dictionary of scrap_type:scrap weight
        yield_model - unpickled yield model
        copper_model - unpickled copper model
        copper_target - production copper target
        scrap_cost - dictionary of scrap_type:scrap cost
    outputs:
        scrap_cost_total - the totaled scrap cost for the commodities
        yield_cost - the cost of lost yield
        copper_cost - the cost of copper (NEEDS WORK)
        value_in_use - the sum of all of these costs
    """
    total_inputs_weight = sum(commodity_inputs.values())
    commodity_inputs_normed = {}
    for c in commodities:
        commodity_inputs_normed[c] = commodity_inputs[c]/total_inputs_weight
    commodity_inputs_normed = pd.DataFrame(commodity_inputs_normed.values()).T
    
    yield_estimate = yield_model.predict(commodity_inputs_normed)
    yield_cost = (1-yield_estimate) * total_inputs_weight * 743.40
    
    copper_estimate = copper_model.predict(commodity_inputs_normed)
    copper_cost = (copper_target - copper_estimate) * 743.40
    
    scrap_cost_total = 0
    for c in commodities:
        scrap_cost_total += commodity_inputs[c] * scrap_cost[c]
    value_in_use = yield_cost + copper_cost + scrap_cost_total
    return scrap_cost_total, yield_cost, copper_cost, value_in_use, copper_estimate, yield_estimate

def run_value_in_use(scrap_orders, commodity_inputs, copper_limit):
    scrap_cost = calculate_scrap_cost(scrap_orders)
    
    yield_model = '../application/pickles/yield_model.pickle'
    yield_model = pickle.load(open(yield_model, 'rb'))

    cu_model = '../application/pickles/copper_model.pickle'
    cu_model = pickle.load(open(cu_model, 'rb'))
    
    return value_in_use(commodity_inputs, yield_model, cu_model, copper_limit, scrap_cost)

if __name__ == '__main__':
    scrap_orders = '../../data/1/scrap_orders.json'
    commodity_inputs = {"bushling":300, "pig_iron":200, "municipal_shred":350, "skulls":200}
    scrap_cost, yield_cost, copper_cost, value_in_use = run_value_in_use(scrap_orders, commodity_inputs, 0.15)
    print('scrap_cost:', scrap_cost)
    print('yield_cost:', yield_cost)
    print('copper_cost:', copper_cost)
    print('value_in_use:', value_in_use)