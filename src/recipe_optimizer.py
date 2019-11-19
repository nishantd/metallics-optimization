import numpy as np
import pandas as pd
from src.helpers.linprog_helper import linprog_lb_wrapper

from src.cu_estimator import CuEstimator


class RecipeOptimizer:
    # internal scraps order
    scraps = ['bushling', 'pig_iron', 'municipal_shred', 'skulls']

    def __init__(self,
                 estimator: CuEstimator,
                 df_constrains: pd.DataFrame,
                 prices: pd.Series,
                 target_gap=0.98) -> None:
        """
        Creates a new recipe optimizer.

        The optimizer uses interior-point method to solve a system of linear equations.
        Current constrains:
         * Cost function = C(x) -> min
         * Mass balance = M(x) >= Heat_Weight
         * Cu amount = Cu(x) <= Cu_Percent
         * Additional mass constrains from the constraints.json
         * Scrap on hand constrains

        Formulas:
         * Cu(x) = bush_mass * cu_amount[bash] + ... + skulls_mass * cu_amount[skulls]
         * M(x) = bush_mass + ... + skulls_mass = Heat_Weight
         * C(x) = bush_mass * price[bash] + ... + skulls_mass * price[skulls]

        :param estimator: Copper amount estimator
        :param df_constrains: data frame with additional constrains
        :param prices: average prices on scrap
        :param target_gap: safety gap so not to exceed the allowable amount of copper.
        """
        self.target_gap = target_gap
        self.estimator = estimator
        self.prices = prices
        self.df_constraints = df_constrains

    @staticmethod
    def get_cost_function(prices):
        """
        Returns the coefficients of the cost function to minimize.

        Cost function operates on average scrap prices.
        """
        return np.array([prices[scrap] for scrap in RecipeOptimizer.scraps])

    @staticmethod
    def get_mass_constraints(expected_mass: int):
        """
        Returns the heat mass constrain.

        Formula:
            Bushling + Pig Iron + Shred + Skulls >= Heat weight
        """
        return 'lb', [1] * len(RecipeOptimizer.scraps), expected_mass

    @staticmethod
    def get_cu_constrains(estimator: CuEstimator, row: pd.Series, gap: float):
        """
        Returns the copper amount constraint.

        Formula:
            Cu(x) = bush_mass * cu_amount[bash] + ...
                + skulls_mass * cu_amount[skulls] <= cu_pct * gap

        :param estimator: Cu content estimator to use.
        :param row: input data to use.
        :param gap: safety gap so not to exceed the allowable amount of copper
        """

        # estimated cu amount per 1 kg of raw scrap
        cu_values = estimator.get_estimated_values(row['steel_grade'])
        cons_a = [cu_values[scrap_type] for scrap_type in RecipeOptimizer.scraps]
        cons_b = row['cu_pct'] * gap

        return 'ub', cons_a, cons_b

    @staticmethod
    def get_inventory_constrains(scrap_inventory: pd.Series):
        """
        Returns scrap on hand constrains.

        We can't use more scrap then we have on hand.

        :param scrap_inventory: the available scrap amount per type.
        """
        scraps = RecipeOptimizer.scraps

        def make_constrain(scrap_type: str, on_hand: float):
            cons_a = [0] * len(scraps)
            idx = scraps.index(scrap_type)
            cons_a[idx] = 1

            cons_b = on_hand

            return 'ub', cons_a, cons_b

        return [make_constrain(scrap_type, on_hand)
                for scrap_type, on_hand in scrap_inventory.items()]

    @staticmethod
    def get_additional_constrains(df: pd.DataFrame):
        """
        Returns additional constrains on the input materials.

        :param df: dataframe with additional constrains.
        """
        scraps = RecipeOptimizer.scraps

        def parse_constrain(row: pd.Series):
            cons_a = [0] * len(scraps)

            idx = scraps.index(row['scrap_type'])
            cons_a[idx] = 1  # constrain for the scrap type
            cons_b = row['weight']

            cons_type = 'lb' if row['type'] == 'minimum' else 'ub'
            return cons_type, cons_a, cons_b

        return [parse_constrain(row) for _, row in df.iterrows()]

    def optimize(self, row: pd.Series, inventory: pd.Series):

        # target weights
        w = self.get_cost_function(self.prices)

        # constrains
        a_ub = []  # left parts of <= constrains
        b_ub = []  # right parts of <= constrains
        a_lb = []  # left  parts of >= constrains
        b_lb = []  # right parts of >= constrains

        constrains = []
        constrains.append(self.get_mass_constraints(row['required_weight']))
        constrains.append(self.get_cu_constrains(self.estimator, row, self.target_gap))
        constrains.extend(self.get_additional_constrains(self.df_constraints))
        constrains.extend(self.get_inventory_constrains(inventory))

        for cons_type, a, b in constrains:
            if cons_type == 'lb':
                a_lb.append(a)
                b_lb.append(b)
            elif cons_type == 'ub':
                a_ub.append(a)
                b_ub.append(b)

        res = linprog_lb_wrapper(w, method='interior-point',
                                 A_ub=a_ub, A_lb=a_lb,
                                 b_ub=b_ub, b_lb=b_lb)

        return dict(zip(self.scraps, res.x))
