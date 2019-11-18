import numpy as np
import pandas as pd
from scipy.optimize import linprog

from src.cu_estimator import CuEstimator


class RecipeOptimizer:
    # scraps order
    scraps = ['bushling', 'pig_iron', 'municipal_shred', 'skulls']

    def __init__(self, estimator: CuEstimator, df_constrains: pd.DataFrame,
                 prices: pd.Series) -> None:
        """
        Creates a new recipe optimizer.

        The optimizer uses simplex method to solve a system of linear equations.
        Current constrains:
         * Cost function = C(x) -> min
         * Mass balance = M(x) = Heat_Weight
         * Cu amount = Cu(x) <= Cu_Percent
         * Additional mass constrains from the constraints.json

        Formulas:
         * Cu(x) = bush_mass * cu_amount[bash] + ... + skulls_mass * cu_amount[skulls]
         * M(x) = bush_mass + ... + skulls_mass = Heat_Weight
         * C(x) = bush_mass * price[bash] + ... + skulls_mass * price[skulls]

        :param estimator: Copper amount estimator
        :param df_constrains: data frame with additional constrains
        :param prices: average prices on scrap
        """
        self.estimator = estimator
        self.prices = prices
        self.df_constraints = df_constrains

    @staticmethod
    def get_cost_function(prices):
        return np.array([prices[scrap] for scrap in RecipeOptimizer.scraps])

    @staticmethod
    def get_mass_constraints(expected_mass: int):
        """
        Returns left and right parts of the heat mass constrain.

        Bushling + Pig Iron + Shred + Skulls = Heat weight
        """
        return [-1] * len(RecipeOptimizer.scraps), -expected_mass

    @staticmethod
    def get_cu_constrains(estimator: CuEstimator, row: pd.Series):
        cu_values = estimator.get_estimated_cu_values(row['steel_grade'])  # per 1 kg
        cons_a = [-cu_values[scrap_type] for scrap_type in RecipeOptimizer.scraps]
        cons_b = row['cu_pct']

        return cons_a, cons_b

    @staticmethod
    def get_additional_constraints(df: pd.DataFrame):
        scraps = RecipeOptimizer.scraps

        def parse_constrain(row: pd.Series):
            cons_a = [0] * len(scraps)

            idx = scraps.index(row['scrap_type'])
            cons_a[idx] = -1  # constrain for the scrap type

            multiplier = -1 if row['type'] == 'minimum' else 1
            cons_b = multiplier * row['weight']
            return cons_a, cons_b

        return (parse_constrain(row) for _, row in df.iterrows())

    def optimize(self, row: pd.Series):
        w = self.get_cost_function(self.prices)

        a_ub = []
        b_ub = []
        a_eq = []
        b_eq = []

        # the mass should be as required
        mass_a, mass_b = self.get_mass_constraints(row['required_weight'])
        a_eq.append(mass_a)
        b_eq.append(mass_b)

        # the scrap amount should be <= additional limits
        for cons_a, cons_b in self.get_additional_constraints(self.df_constraints):
            a_ub.append(cons_a)
            b_ub.append(cons_b)

        # Cu content should be <= expected amount
        cons_a, cons_b = self.get_cu_constrains(self.estimator, row)
        a_ub.append(cons_a)
        b_ub.append(cons_b)

        res = linprog(w, A_eq=a_eq, b_eq=b_eq, A_ub=a_ub, b_ub=b_ub, bounds=(0, None),
                      method='simplex')
        return res
