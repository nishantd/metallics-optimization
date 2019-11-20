import argparse
import json

from src.cu_estimator import CuEstimator
from src.data_loader import DataLoader
from src.recipe_optimizer import RecipeOptimizer
from src.yield_estimator import YieldEstimator


def parse_args(args=None):
    parser = argparse.ArgumentParser(description="This util helps to generate heat recipes.")
    parser.add_argument('path', help='Path to the input data folder.')
    parser.add_argument('--mass-factor', help='safety gap for the heat weight', type=float,
                        default=1.01)
    parser.add_argument('--cu-factor', help='safety gap for the copper amount', type=float,
                        default=0.98)
    return parser.parse_args(args)


def _main(args):
    # load input data
    data_loader = DataLoader(args.path)

    df_prod = data_loader.df_previous_production
    df_constrains = data_loader.df_constrains
    scrap_prices = data_loader.scrap_prices
    scrap_inventory = data_loader.scrap_inventory
    prod_schedule = data_loader.production_schedule

    # fit estimators
    cu_estimator = CuEstimator()
    cu_estimator.fit(df_prod)

    yield_estimator = YieldEstimator()
    yield_estimator.fit(df_prod)

    optimizer = RecipeOptimizer(cu_estimator=cu_estimator,
                                yield_estimator=yield_estimator,
                                df_constrains=df_constrains,
                                prices=scrap_prices,
                                cu_target_gap=args.cu_factor,
                                heat_weight_gap=args.mass_factor)

    results = []
    for idx, row in prod_schedule.iterrows():
        recipe = optimizer.optimize(row, scrap_inventory)

        # update scrap on hand
        for scrap_type, value in recipe.items():
            scrap_inventory[scrap_type] = max(0, scrap_inventory[scrap_type] - value)

        recipe_with_steel_grade = dict(recipe)
        recipe_with_steel_grade.update({'steel_grade': row['steel_grade']})

        results.append({
            'heat_seq': row['heat_seq'],
            'heat_id': row['heat_id'],
            'steel_grade': row['steel_grade'],
            'predicted_tap_weight': yield_estimator.predict(recipe_with_steel_grade),
            'predicted_chemistry': {
                'cu_pct': cu_estimator.predict(recipe_with_steel_grade)
            },
            'suggested_recipe': recipe
        })

    print(json.dumps(results))


if __name__ == '__main__':
    args = parse_args()
    _main(args)
