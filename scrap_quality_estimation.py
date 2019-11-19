##
import pandas as pd
import json
import glob
import os
import numpy
from sklearn.linear_model import Lasso
from tabulate import tabulate


def scrap_quality_estimation(df_chem, df_order, df_inven, components):
    """
    this funtion will estimate the quality of the scrap by estimating the portion of copper and yield in the scrap
     component
    :param df_chem: dataframe containing the chemical component of the scrap
    :param df_order: dataframe contaning the order history with the price of the scrape
    :param: df_inven: dataframe contaning the inventory storage of the scrape
    :param components: an list with the scrap component
    :return: results_df : dataframe with Component, cu_pct, price_per_ton, yield, inv_weight
    """
    # the portion of the total evaporated material
    lost_portion = 1 - df_chem["yield"].values

    # the portion of the evaporated material in every scrap material

    the_component_por = df_chem[components].values

    lost_share_per_component = Lasso(alpha=0.00001, fit_intercept=False, precompute=True, positive=True)
    lost_share_per_component.fit(the_component_por, lost_portion)
    # portion of yield in every component
    yield_coef = 1 - lost_share_per_component.coef_

    yield_ = df_chem[components].values * yield_coef
    # total copper portion in the whol scrap
    total_copper_port= df_chem["cu_pct"].values
    # copper portion in every component
    copper_port = Lasso(alpha=0.00001, fit_intercept=False, precompute=True, positive=True)
    copper_port.fit(yield_, total_copper_port)

    copperport = copper_port.coef_

    price_per_ton = numpy.zeros(len(components))
    ind = 0
    # claculate the av price per ton payed for the scrap in the inv
    for component in components:
        df = df_order[df_order['scrap_type'] == component][['weight', 'price_per_ton']]
        p = df['price_per_ton'].values
        w = df['weight'].values
        price_per_ton[ind] = sum(p * w) / sum(w)
        ind = ind + 1

    inv_weight = df_inven['weight'].values
    results_df = pd.DataFrame({'Component': component, 'cu_pct': copperport,
                               'price_per_ton': price_per_ton,'yield': yield_coef, 'inv_weight': inv_weight})
    print(tabulate(results_df))
    return results_df
