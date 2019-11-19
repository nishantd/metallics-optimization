import json
import sys


# Scrap types
BUSHELING = "bushling"
PIG_IRON = "pig_iron"
SHRED = "municipal_shred"
SKULLS = "skulls"
# Status of order
DELIVERED = "delivered"


def get_scrap_purchases(file_location):
    with open(file_location) as orders_file:
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


if __name__ == "__main__":
    get_scrap_purchases(sys.argv[1])
