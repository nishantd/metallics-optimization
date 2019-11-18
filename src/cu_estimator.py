import pandas as pd
from scipy.optimize import least_squares


class CuEstimator:

    def __init__(self,
                 x0=(0.05, 0.001, 0.1, 0.04),
                 bounds=([0, 0, 0, 0], [100, 100, 100, 100])) -> None:
        self.x0 = x0
        self.bounds = bounds
        self._estimators = {}

    @staticmethod
    def cost_function(x, df: pd.DataFrame):
        return [
            row['bushling'] * x[0]
            + row['pig_iron'] * x[1]
            + row['municipal_shred'] * x[2]
            + row['skulls'] * x[3]
            - row['cu_pct']
            for _, row in df.iterrows()
        ]

    @staticmethod
    def calc_function(x, row: pd.Series):
        return row['bushling'] * x[0] \
               + row['pig_iron'] * x[1] \
               + row['municipal_shred'] * x[2] \
               + row['skulls'] * x[3]

    def fit(self, df):
        self._estimators = {}

        for steel_grade, data in df.groupby('steel_grade'):
            values = least_squares(lambda x: self.cost_function(x, data), self.x0,
                                   bounds=self.bounds).x

            self._estimators.update({steel_grade: values})

    def predict(self, row: pd.Series):
        steel_grade = row['steel_grade']
        if steel_grade not in self._estimators:
            raise ValueError(f'Steel grade {steel_grade} has no estimator yet.'
                             f'Use `fit` method first.')

        values = self._estimators[steel_grade]
        return self.calc_function(values, row)

    def get_estimated_cu_values(self, steel_grade: str):
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
