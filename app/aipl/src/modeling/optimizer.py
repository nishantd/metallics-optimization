import numpy as np
import os
import sys
from cvxopt import matrix, spmatrix, sparse, solvers

sys.path.insert(0, os.path.abspath("aipl/src"))
from etl.ingestion import get_scrap_prices
from etl.ingestion import get_scrap_inventory
from etl.ingestion import get_upcoming_heats
from modeling.cu_predictor import get_cu_per_scraptype


# Scrap types
BUSHELING = "bushling"
PIG_IRON = "pig_iron"
SHRED = "municipal_shred"
SKULLS = "skulls"
SCRAP_TYPES = [BUSHELING, PIG_IRON, SHRED, SKULLS]
REQD_WEIGHT = "required_weight"
CHEM = "chemistry"
CU_PCT = "cu_pct"
# Data file locations
DATA_DIR = r"../data/1/"
SCRAP_ORDERS_DATAFILE = os.path.join(DATA_DIR, "scrap_orders.json")
SCRAP_INV_DATAFILE = os.path.join(DATA_DIR, "scrap_inventory.json")
PRODUCTION_SCHEDULE_DATA_FILE = os.path.join(DATA_DIR, "production_schedule.json")


def get_cost_of_recipe(busheling_wt, pigiron_wt, shred_wt, skulls_wt):
    """Calculates the cost of provided scrap-mix based on average scrap prices
    """
    # Eventually implement FIFO-layering cost here
    scrap_prices = get_scrap_prices(SCRAP_ORDERS_DATAFILE)
    cost_of_recipe = (
        (scrap_prices[BUSHELING] * busheling_wt)
        + (scrap_prices[PIG_IRON] * pigiron_wt)
        + (scrap_prices[SHRED] * shred_wt)
        + (scrap_prices[SKULLS] * skulls_wt)
    )
    return cost_of_recipe


def get_value_in_use_for_recipe(busheling_wt, pigiron_wt, shred_wt, skulls_wt):
    """Calculates the value-in-use ($) for provided scrap-mix

    Params:
    busheling_wt - Weight of busheling scrap
    pigiron_wt - Weight of pig iron
    shred_wt - Weight of shred scrap
    skulls_wt - Weight of skulls scrap
    """
    # Arguments can be generalized in the future
    return get_cost_of_recipe(busheling_wt, pigiron_wt, shred_wt, skulls_wt)
    # + get_cost_of_yield_loss(busheling_wt, pigiron_wt, shred_wt, skulls_wt)


def get_optimal_recipes():
    """Assigns an optimal recipe to all the upcoming heats present in the
    production schedule
    """
    # minimize cost over a sequence of heats
    upcoming_heats = get_upcoming_heats(PRODUCTION_SCHEDULE_DATA_FILE)

    # Formulate objective function
    scrap_prices = get_scrap_prices(SCRAP_ORDERS_DATAFILE)
    scrap_prices_st = [scrap_prices[st] for st in SCRAP_TYPES]
    obj_function_c = matrix(scrap_prices_st * len(upcoming_heats))

    # Setup constraints
    # Cu limit constraint
    cu_coefficients = get_cu_per_scraptype()
    cu_constraint_G = spmatrix(
        [cu_coefficients[st] / 100 for st in SCRAP_TYPES] * len(upcoming_heats),
        np.repeat(np.arange(len(upcoming_heats)), len(SCRAP_TYPES)),
        np.arange(len(SCRAP_TYPES) * len(upcoming_heats)),
        (len(upcoming_heats), len(SCRAP_TYPES) * len(upcoming_heats)),
    )
    cu_heats_h = matrix(
        [
            upcoming_heats.iloc[heat][REQD_WEIGHT]
            * upcoming_heats.iloc[heat][CHEM][CU_PCT]
            / 100
            for heat in upcoming_heats.index
        ]
    )

    # Available inventory constraint
    inv_constraint_G = spmatrix(
        np.ones(len(SCRAP_TYPES) * len(upcoming_heats)),
        np.tile(np.arange(len(SCRAP_TYPES)), len(upcoming_heats)),
        np.arange(len(SCRAP_TYPES) * len(upcoming_heats)),
        (len(SCRAP_TYPES), len(SCRAP_TYPES) * len(upcoming_heats)),
    )
    available_inv = get_scrap_inventory(SCRAP_INV_DATAFILE, SCRAP_ORDERS_DATAFILE)
    available_inv_h = matrix([int(available_inv[st]) for st in SCRAP_TYPES])

    # Required liquid steel constraint
    reqd_weight_constraint_G = spmatrix(
        np.ones(len(SCRAP_TYPES) * len(upcoming_heats)),
        np.repeat(np.arange(len(upcoming_heats)), len(SCRAP_TYPES)),
        np.arange(len(SCRAP_TYPES) * len(upcoming_heats)),
        (len(upcoming_heats), len(SCRAP_TYPES) * len(upcoming_heats)),
    )
    reqd_weights_h = matrix(upcoming_heats[REQD_WEIGHT])

    # Combine constraints together
    final_constraints_G = sparse(
        [cu_constraint_G, inv_constraint_G, reqd_weight_constraint_G]
    )
    final_constraints_h = matrix([cu_heats_h, available_inv_h, reqd_weights_h])

    # Optimize to get recipes
    # sol = solvers.lp(obj_function_c, final_constraints_G, final_constraints_h)
    # print(sol["x"])

    # TODO: Temporary placeholder as lp solver giving an error
    optimal_recipe_placeholder = (
        "{BUSHELING: 250, PIG_IRON: 250, SHRED: 300, SKULLS: 200}"
    )
    upcoming_heats["recipe"] = optimal_recipe_placeholder

    # Return production schedule with recipe column
    return upcoming_heats


if __name__ == "__main__":
    print("Recipes for upcoming schedule\n{}".format(get_optimal_recipes()))
    print(
        "Value-in-use for recipe: ${0:.2f}".format(
            get_value_in_use_for_recipe(250, 250, 300, 200)
        )
    )
