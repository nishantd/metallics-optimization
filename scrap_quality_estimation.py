##
import pandas as pd
import json
import glob
import os
import numpy
from sklearn.linear_model import Lasso

def scrap_quality_estimation(df_chem, df_order,df_inven):
    """
    this funtion will estimate the quality of the scrap by estimating the portion of copper and yield in the scrap
     component
    :param df_chem: dataframe containing the chemical component of the scrap
    :param df_order: dataframe contaning the order history with the price of the scrape
    :return: results_df : dataframe with Component, cu_pct, price_per_ton, yield, inv_weight
    """
    # the portion of the total evaporated material
    lost_portion = 1 - df_chem["yield"].values

    # the portion of the evaporated material in every scrap material
    the_component_por = df_chem[["bushling", "pig_iron", "municipal_shred", "skulls"]].values

    lost_share_per_component = Lasso(alpha=0.00001, fit_intercept=False, precompute=True, positive=True)
    lost_share_per_component.fit(the_component_por, lost_portion)
    # portion of yield in every component
    yield_coef = 1 - lost_share_per_component.coef_

    yield_ = df_chem[["bushling", "pig_iron", "municipal_shred", "skulls"]].values * yield_coef
    # total copper portion in the whol scrap
    total_copper_port= df_chem["cu_pct"].values
    # copper portion in every component
    copper_port = Lasso(alpha=0.00001, fit_intercept=False, precompute=True, positive=True)
    copper_port.fit(yield_, total_copper_port)

    copperport = copper_port.coef_

    price_per_ton = numpy.zeros(4)
    ind = 0
    # claculate the av price per ton payed for the scrap in the inv
    for component in df_order['scrap_type'].drop_duplicates(keep='first').values:
        df = df_order[df_order['scrap_type'] == component][['weight', 'price_per_ton']]
        p = df['price_per_ton'].values
        w = df['weight'].values
        price_per_ton[ind] = sum(p * w) / sum(w)
        ind = ind + 1

    inv_weight = df_inven['weight'].values
    results_df = pd.DataFrame({'Component': ["bushling", "pig_iron", "municipal_shred", "skulls"], 'cu_pct': copperport,
                               'price_per_ton': price_per_ton,'yield': yield_coef, 'inv_weight': inv_weight})
    return results_df
