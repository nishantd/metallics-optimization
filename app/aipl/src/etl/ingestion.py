import json
import sys


# Scrap types
BUSHELING = "bushling"
PIG_IRON = "pig_iron"
SHRED = "municipal_shred"
SKULLS = "skulls"
# Status of order
DELIVERED = "delivered"
ON_HAND = "on_hand"


def get_scrap_purchases(order_data_file):
    """Load scrap orders - we are not messing with dates currently and
    are assuming all deliveries are unused

    Parameters:
        order_data_file: Location of scrap orders data
    """

    with open(order_data_file) as orders_file:
        orders = json.load(orders_file)

    busheling_orders = []
    pigiron_orders = []
    shred_orders = []
    skulls_orders = []

    for o in orders:
        if o["status"] == DELIVERED:
            if o["scrap_type"] == BUSHELING:
                busheling_orders.append(o["price_per_ton"])
            elif o["scrap_type"] == PIG_IRON:
                pigiron_orders.append(o["price_per_ton"])
            elif o["scrap_type"] == SHRED:
                shred_orders.append(o["price_per_ton"])
            elif o["scrap_type"] == SKULLS:
                skulls_orders.append(o["price_per_ton"])

    return {
        BUSHELING: busheling_orders,
        PIG_IRON: pigiron_orders,
        SHRED: shred_orders,
        SKULLS: skulls_orders,
    }


def get_scrap_inventory(inv_data_file, order_data_file):
    """Load scrap inventory - we are not messing with dates currently and
    are assuming all deliveries are unused

    Parameters:
        inv_data_file: Location of scrap inventory data
        order_data_file: Location of scrap orders data
    """

    with open(inv_data_file) as inv_file:
        inventory = json.load(inv_file)
    with open(order_data_file) as orders_file:
        orders = json.load(orders_file)

    busheling_weight = 0.0
    pigiron_weight = 0.0
    shred_weight = 0.0
    skulls_weight = 0.0

    # Add available inventory
    for i in inventory:
        if i["status"] == ON_HAND:
            if i["scrap_type"] == BUSHELING:
                busheling_weight += i["weight"]
            elif i["scrap_type"] == PIG_IRON:
                pigiron_weight += i["weight"]
            elif i["scrap_type"] == SHRED:
                shred_weight += i["weight"]
            elif i["scrap_type"] == SKULLS:
                skulls_weight += i["weight"]

    # Add delivered scrap inventory
    for o in orders:
        if o["status"] == DELIVERED:
            if o["scrap_type"] == BUSHELING:
                busheling_weight += i["weight"]
            elif o["scrap_type"] == PIG_IRON:
                pigiron_weight += i["weight"]
            elif o["scrap_type"] == SHRED:
                shred_weight += i["weight"]
            elif o["scrap_type"] == SKULLS:
                skulls_weight += i["weight"]

    return {
        BUSHELING: busheling_weight,
        PIG_IRON: pigiron_weight,
        SHRED: shred_weight,
        SKULLS: skulls_weight,
    }


if __name__ == "__main__":
    get_scrap_purchases(sys.argv[1])
