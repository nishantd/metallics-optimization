import os, sys
import logging
import json

import copper_model
import yield_model
import cost_estimator
import recipe_optimizer

logging.basicConfig()
log = logging.getLogger()
log.setLevel(20)

def main():
    if not len(sys.argv) == 2:
        print(sys.stderr, 'usage: generate_recipes.py <data_dir>')
        sys.exit(1)

    data_dir = sys.argv[1]
    log.info(data_dir)

    cu_model = copper_model.CopperModel(data_dir)
    cu_model.create_model()

    y_model = yield_model.YieldModel(data_dir)
    y_model.create_model()

    cost_es = cost_estimator.CostEstimator(data_dir)
    cost_es.initialize()

    ro = recipe_optimizer.RecipeOptimizer(
        data_dir=data_dir, copper_model=cu_model, yield_model=yield_model,
        cost_estimator=cost_es)
    ro.initialize()
    schedule_recipes = ro.create_recipes_for_schedule()

    print(json.dumps(schedule_recipes))


if __name__ == '__main__':
    main()

