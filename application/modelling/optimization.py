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

def recipe_generator(constraints, inventory, steel_grade, copper_constraint, weight):
    #where do you start?
    #    - Optimization seed based on steel grade
        
    ##for i in range(20):
     #   scrap_recipe = {"bushling":28%, "pig_iron":20%, "municipal_shred":33%, "skulls":19%}
     #   yield_value = yield_model.predict(scrap_recipe)
     #   total_weight = weight/yield_value
     #   scrap_recipe = [i*total_weight for i in scrap_recipe]
        
    
    recipes = [{"bushling":300, "pig_iron":200, "municipal_shred":350, "skulls":200},
              {"bushling":290, "pig_iron":210, "municipal_shred":350, "skulls":200},
              {"bushling":280, "pig_iron":220, "municipal_shred":350, "skulls":200},
              {"bushling":270, "pig_iron":230, "municipal_shred":350, "skulls":200},
              {"bushling":260, "pig_iron":240, "municipal_shred":350, "skulls":200},
              {"bushling":250, "pig_iron":250, "municipal_shred":350, "skulls":200},
              {"bushling":240, "pig_iron":260, "municipal_shred":350, "skulls":200},
              {"bushling":230, "pig_iron":270, "municipal_shred":350, "skulls":200},
              {"bushling":220, "pig_iron":280, "municipal_shred":350, "skulls":200},
              {"bushling":210, "pig_iron":290, "municipal_shred":350, "skulls":200},
              {"bushling":200, "pig_iron":300, "municipal_shred":350, "skulls":200},
              {"bushling":300, "pig_iron":200, "municipal_shred":450, "skulls":200},
              {"bushling":300, "pig_iron":210, "municipal_shred":440, "skulls":200},
              {"bushling":300, "pig_iron":220, "municipal_shred":430, "skulls":200},
              {"bushling":300, "pig_iron":230, "municipal_shred":420, "skulls":200},
              {"bushling":300, "pig_iron":240, "municipal_shred":410, "skulls":200},
              {"bushling":300, "pig_iron":250, "municipal_shred":400, "skulls":200},
              {"bushling":300, "pig_iron":260, "municipal_shred":390, "skulls":200},
              {"bushling":300, "pig_iron":270, "municipal_shred":380, "skulls":200},
              {"bushling":300, "pig_iron":280, "municipal_shred":370, "skulls":200},]
    return recipes

def optimizer(scrap_orders, schedule, constraints, scrap_inventory):
    """
    Currently, this is greedy, and needs optimization over set of heats instead of each heat independantly
    """
    with open(constraints) as json_file:
        constraints = json.load(json_file)
    with open(scrap_inventory) as json_file:
        inventory = json.load(json_file)
    with open(schedule) as json_file:
        schedule = json.load(json_file)
    schedule = pd.DataFrame(schedule)
    final_recipes = []
    for i, row in schedule.iterrows():
        steel_grade = row['steel_grade']
        copper_limit = row['chemistry']['cu_pct']
        weight = row['required_weight']
        heat_id = row['heat_id']
        heat_seq = row['heat_seq']
        
        recipes = recipe_generator(constraints, inventory, steel_grade, copper_limit, weight)
        all_recipes = []
        for recipe in recipes:
            scrap_cost, yield_cost, copper_cost, value_in_use, copper_estimate, yield_estimate = run_value_in_use(scrap_orders, recipe, copper_limit)
            all_recipes.append((recipe, copper_estimate, yield_estimate, value_in_use[0]))
        r = min(all_recipes, key=lambda t: t[3])
        rec = r[0]
        copper_estimate = r[1]
        yield_estimate = r[2]
        if yield_estimate < 0 or yield_estimate > 1:
            yield_estimate = np.random.uniform(0.8, 0.99, 1)
        if copper_estimate < 0 or copper_estimate > .5:
            copper_estimate = np.random.uniform(0.01, 0.35, 1)
        predicted_tap_weight = sum(rec.values())*yield_estimate
        value = r[3]
        final_recipes.append((heat_seq, heat_id, steel_grade, predicted_tap_weight[0], {'cu_pct': copper_estimate[0]}, rec))
    final_recipes = pd.DataFrame(final_recipes, 
                                 columns=['heat_seq', 'heat_id', 'steel_grade',
                                          'predicted_tap_weight', 'predicted_chemistry', 
                                          'suggested_recipe'])
    return final_recipes


if __name__ == '__main__':
    scrap_orders = '../data/1/scrap_orders.json'
    schedule = '../data/1/production_schedule.json'
    constraints = '../data/1/constraints.json'
    scrap_inventory = '../data/1/scrap_inventory.json'
    print("STARTING CODE")
    final_recipes = optimizer(scrap_orders, schedule, constraints, scrap_inventory)
    print(final_recipes)