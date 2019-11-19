from cvxopt import matrix

def get_value_in_use_for_recipe(busheling, pigiron, shred, skulls):
    return get_cost_of_recipe(busheling, pigiron, shred, skulls)\
           + get_cost_of_yield_loss(busheling, pigiron, shred, skulls)

def get_optimal_recipes():
    # minimize cost over a sequence of heats


    # setup constraints
    cu_for_recipe = get_cu_for_scraptype('busheling')\
                    + get_cu_for_scraptype('pigiron')\
                    + get_cu_for_scraptype('shred')\
                    + get_cu_for_scraptype('skulls')

    available_inventory

    return (busheling, pigiron, shred, skulls)