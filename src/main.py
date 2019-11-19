import json
import os

import pandas as pd
from pandas.io.json import json_normalize

from definitions import PATH_DATA_DIRECTORY
from src.cu_estimator import CuEstimator
from src.data_loader import DataLoader
from src.yield_estimator import YieldEstimator

data_loader = DataLoader(os.path.join(PATH_DATA_DIRECTORY, '1'))
estimator = YieldEstimator()
estimator.fit(data_loader.df_previous_production)

print(estimator.get_estimated_values('ST1'))

# with open('data/1/previous_heats_with_properties.json') as f:
#     data = json.load(f)
# df = json_normalize(data)
# df = df.rename(columns=lambda col: col.rpartition('.')[-1])
#
# estimator = CuEstimator()
# estimator.fit(df)
#
# row = df.iloc[0]
# print(estimator.predict(row))


# from src.data_loader import DataLoader
# from src.recipe_optimizer import RecipeOptimizer
# from definitions import PATH_DATA_DIRECTORY
#
# data_loader = DataLoader(os.path.join(PATH_DATA_DIRECTORY, '1'))
# df_prod = data_loader.df_previous_production
# df_constrains = data_loader.df_constrains
# scrap_prices = data_loader.scrap_prices
# scrap_inventory = data_loader.scrap_inventory
#
# estimator = CuEstimator()
# estimator.fit(df_prod)
#
# fake_inventory = pd.Series(
#     {'bushling': 1000.0, 'pig_iron': 1000.0, 'municipal_shred': 1000.0, 'skulls': 1500.0})
#
# recipe_optimizer = RecipeOptimizer(estimator, df_constrains, scrap_prices)
# row = df_prod.iloc[0]
#
# recipe_optimizer.optimize(row, fake_inventory)
