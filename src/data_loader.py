import json
import os

import pandas as pd
from pandas.io.json import json_normalize


class DataLoader:
    def __init__(self, folder_path: str) -> None:
        self.folder_path = folder_path

    @staticmethod
    def _load_df(path: str):
        with open(path) as f:
            data = json.load(f)
        df = json_normalize(data)
        df = df.rename(columns=lambda col: col.rpartition('.')[-1])
        return df

    @property
    def df_previous_production(self):
        return self._load_df(os.path.join(self.folder_path, 'previous_heats_with_properties.json'))

    @property
    def df_constrains(self):
        with open(os.path.join(self.folder_path, 'constraints.json')) as f:
            data = json.load(f)['scrap_type_constraints_per_heat']
        df_cons = pd.DataFrame(data)

        # we have 'bushling', not 'bushlings' in all other cases
        df_cons = df_cons.replace('bushlings', 'bushling')

        return df_cons

    @property
    def scrap_prices(self):
        df_orders = self._load_df(os.path.join(self.folder_path, 'scrap_orders.json'))
        df_orders['price_per_kg'] = df_orders['price_per_ton'] / 1000
        prices = df_orders.groupby('scrap_type')['price_per_kg'].mean()

        return prices

    @property
    def scrap_inventory(self):
        df_inventory = self._load_df(os.path.join(self.folder_path, 'scrap_inventory.json'))
        df_inventory = df_inventory[df_inventory['status'] == 'on_hand']
        df_inventory.set_index('scrap_type', inplace=True)
        scrap_inventory = df_inventory['weight'].to_dict()

        return scrap_inventory

    @property
    def production_schedule(self):
        return self._load_df(os.path.join(self.folder_path, 'production_schedule.json'))
