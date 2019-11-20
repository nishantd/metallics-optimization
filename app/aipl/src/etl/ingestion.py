import pandas as pd
import sys


# Scrap types
BUSHELING = "bushling"
PIG_IRON = "pig_iron"
SHRED = "municipal_shred"
SKULLS = "skulls"
# Status of order
DELIVERED = "delivered"
ON_HAND = "on_hand"


def get_scrap_prices(order_data_file):
    """Load scrap orders - we are not messing with dates currently and
    are assuming all deliveries are unused

    Parameters:
        order_data_file: Location of scrap orders data
    """
    # Load scrap orders that have already been delivered
    orders = pd.read_json(order_data_file)
    orders = orders[orders.status == DELIVERED]

    # Get average prices per scrap type from scrap orders
    busheling_price = orders[orders.scrap_type == BUSHELING].price_per_ton.mean()
    pigiron_price = orders[orders.scrap_type == PIG_IRON].price_per_ton.mean()
    shred_price = orders[orders.scrap_type == SHRED].price_per_ton.mean()
    skulls_price = orders[orders.scrap_type == SKULLS].price_per_ton.mean()

    return {
        BUSHELING: busheling_price,
        PIG_IRON: pigiron_price,
        SHRED: shred_price,
        SKULLS: skulls_price,
    }


def get_scrap_inventory(inv_data_file, order_data_file):
    """Load scrap inventory - we are not messing with dates currently and
    are assuming all deliveries are unused

    Parameters:
        inv_data_file: Location of scrap inventory data
        order_data_file: Location of scrap orders data
    """
    # Load on-hand available inventory
    inventory = pd.read_json(inv_data_file)
    inventory = inventory[inventory.status == ON_HAND]
    # Load scrap orders that have been delivered
    orders = pd.read_json(order_data_file)
    orders = orders[orders.status == DELIVERED]

    busheling_weight = (
        inventory[inventory.scrap_type == BUSHELING].weight.sum()
        + orders[orders.scrap_type == BUSHELING].weight.sum()
    )
    pigiron_weight = (
        inventory[inventory.scrap_type == PIG_IRON].weight.sum()
        + orders[orders.scrap_type == PIG_IRON].weight.sum()
    )
    shred_weight = (
        inventory[inventory.scrap_type == SHRED].weight.sum()
        + orders[orders.scrap_type == SHRED].weight.sum()
    )
    skulls_weight = (
        inventory[inventory.scrap_type == SKULLS].weight.sum()
        + orders[orders.scrap_type == SKULLS].weight.sum()
    )

    return {
        BUSHELING: busheling_weight,
        PIG_IRON: pigiron_weight,
        SHRED: shred_weight,
        SKULLS: skulls_weight,
    }


def get_upcoming_heats(production_schedule_data_file):
    """Fetch the upcoming heats from the production schedule

    Params:
    production_schedule_data_file - Location of production schedule data
    """
    # Load production schedule data
    schedule = pd.read_json(production_schedule_data_file)
    return schedule


if __name__ == "__main__":
    pass
