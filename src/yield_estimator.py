import pandas as pd
from scipy.optimize import least_squares


class YieldEstimator:
    """
    This class helps to estimate yield (in %) of the scraps.
    """

    def __init__(self,
                 x0=(0.9, 0.99, 0.95, 0.89),
                 bounds=([0, 0, 0, 0], [1, 1, 1, 1])) -> None:
        self.x0 = x0
        self.bounds = bounds
        self._estimators = {}

    @staticmethod
    def _loss(x, df: pd.DataFrame):
        """
        Calculates the loss value for the given records

        Loss is the expected heat weight - tap weight.
        """
        return [
            row['bushling'] * x[0]
            + row['pig_iron'] * x[1]
            + row['municipal_shred'] * x[2]
            + row['skulls'] * x[3]
            - row['tap_weight']
            for _, row in df.iterrows()
        ]

    @staticmethod
    def _calc(x, row: dict):
        """
        Calculate expected weight for the given recipe.

        :param x: estimated amount of copper per each scrap type.
        :param row: the recipe.
        """
        return row['bushling'] * x[0] \
               + row['pig_iron'] * x[1] \
               + row['municipal_shred'] * x[2] \
               + row['skulls'] * x[3]

    def fit(self, df: pd.DataFrame):
        """
        Fits estimator on th `df` data frame.

        :param df: The data frame with previous heats and their props.
        """
        self._estimators = {}

        for steel_grade, data in df.groupby('steel_grade'):
            values = least_squares(lambda x: self._loss(x, data), self.x0,
                                   bounds=self.bounds).x

            self._estimators.update({steel_grade: values})

    def predict(self, row: dict):
        """
        Predicts yield the input scrap types.

        :param row: Series with the `steel_grade` and recipe of the heat to predict.
        :return: estimated yield per scrap type for the recipe.
        """
        steel_grade = row['steel_grade']
        if steel_grade not in self._estimators:
            raise ValueError(f'Steel grade {steel_grade} has no estimator yet.'
                             f'Use `fit` method first.')

        values = self._estimators[steel_grade]
        return self._calc(values, row)

    def get_estimated_values(self, steel_grade: str):
        """
        Returns estimated yield for raw material.
        :param steel_grade: the requested steel grade.
        :return: dictionary with results.
        """
        if steel_grade not in self._estimators:
            raise ValueError(f'Steel grade {steel_grade} has no estimator yet.'
                             f'Use `fit` method first.')
        values = self._estimators[steel_grade]
        return {
            'bushling': values[0],
            'pig_iron': values[1],
            'municipal_shred': values[2],
            'skulls': values[3]
        }
