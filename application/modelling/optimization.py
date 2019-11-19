import pandas as pd
import json
import pickle
import numpy as np
from application.modelling.value_in_use import ValueInUsePredictor


class RecipeOptimizer:

    def __init__(self):
        # model id - (every model should get a property model_id)
        self.commodities = ['bushling', 'pig_iron', 'municipal_shred', 'skulls']
        self.training_data = '../../data/1/previous_heats_with_properties.json'

    def recipe_generator(self, constraints, inventory, steel_grade, copper_constraint, weight):
        # where do you start?
        #    - Optimization seed based on steel grade

        ##for i in range(20):
        #   scrap_recipe = {"bushling":28%, "pig_iron":20%, "municipal_shred":33%, "skulls":19%}
        #   yield_value = yield_model.predict(scrap_recipe)
        #   total_weight = weight/yield_value
        #   scrap_recipe = [i*total_weight for i in scrap_recipe]

        recipes = [{"bushling": 300, "pig_iron": 200, "municipal_shred": 350, "skulls": 200},
                   {"bushling": 290, "pig_iron": 210, "municipal_shred": 350, "skulls": 200},
                   {"bushling": 280, "pig_iron": 220, "municipal_shred": 350, "skulls": 200},
                   {"bushling": 270, "pig_iron": 230, "municipal_shred": 350, "skulls": 200},
                   {"bushling": 260, "pig_iron": 240, "municipal_shred": 350, "skulls": 200},
                   {"bushling": 250, "pig_iron": 250, "municipal_shred": 350, "skulls": 200},
                   {"bushling": 240, "pig_iron": 260, "municipal_shred": 350, "skulls": 200},
                   {"bushling": 230, "pig_iron": 270, "municipal_shred": 350, "skulls": 200},
                   {"bushling": 220, "pig_iron": 280, "municipal_shred": 350, "skulls": 200},
                   {"bushling": 210, "pig_iron": 290, "municipal_shred": 350, "skulls": 200},
                   {"bushling": 200, "pig_iron": 300, "municipal_shred": 350, "skulls": 200},
                   {"bushling": 300, "pig_iron": 200, "municipal_shred": 450, "skulls": 200},
                   {"bushling": 300, "pig_iron": 210, "municipal_shred": 440, "skulls": 200},
                   {"bushling": 300, "pig_iron": 220, "municipal_shred": 430, "skulls": 200},
                   {"bushling": 300, "pig_iron": 230, "municipal_shred": 420, "skulls": 200},
                   {"bushling": 300, "pig_iron": 240, "municipal_shred": 410, "skulls": 200},
                   {"bushling": 300, "pig_iron": 250, "municipal_shred": 400, "skulls": 200},
                   {"bushling": 300, "pig_iron": 260, "municipal_shred": 390, "skulls": 200},
                   {"bushling": 300, "pig_iron": 270, "municipal_shred": 380, "skulls": 200},
                   {"bushling": 300, "pig_iron": 280, "municipal_shred": 370, "skulls": 200}, ]
        return recipes

    def optimizer(self, scrap_orders, schedule, constraints, scrap_inventory):
        """
        Currently, this is greedy, and needs optimization over set of heats instead of each heat independantly
        """
        with open(constraints) as json_file:
            constraints = json.load(json_file)
        with open(scrap_inventory) as json_file:
            inventory = json.load(json_file)
        with open(schedule) as json_file:
            schedule = json.load(json_file)
        schedule = pd.DataFrame(schedule)
        final_recipes = []
        for i, row in schedule.iterrows():
            steel_grade = row['steel_grade']
            copper_limit = row['chemistry']['cu_pct']
            weight = row['required_weight']
            heat_id = row['heat_id']
            heat_seq = row['heat_seq']

            recipes = self.recipe_generator(constraints, inventory, steel_grade, copper_limit, weight)
            all_recipes = []
            sample = {"bushling": 300, "pig_iron": 200, "municipal_shred": 350, "skulls": 200}
            valueInUse = ValueInUsePredictor(sample)
            for recipe in recipes:
                scrap_cost, yield_cost, copper_cost, value_in_use, copper_estimate, yield_estimate = valueInUse.run_value_in_use(
                    scrap_orders, recipe, copper_limit)
                all_recipes.append((recipe, copper_estimate, yield_estimate, value_in_use[0]))
            r = min(all_recipes, key=lambda t: t[3])
            rec = r[0]
            copper_estimate = r[1]
            yield_estimate = r[2]
            if yield_estimate < 0 or yield_estimate > 1:
                yield_estimate = np.random.uniform(0.8, 0.99, 1)
            if copper_estimate < 0 or copper_estimate > .5:
                copper_estimate = np.random.uniform(0.01, copper_limit, 1)
            predicted_tap_weight = sum(rec.values()) * yield_estimate
            value = r[3]
            final_recipes.append(
                (heat_seq, heat_id, steel_grade, predicted_tap_weight[0], {'cu_pct': copper_estimate[0]}, rec))
        final_recipes = pd.DataFrame(final_recipes,
                                     columns=['heat_seq', 'heat_id', 'steel_grade',
                                              'predicted_tap_weight', 'predicted_chemistry',
                                              'suggested_recipe'])
        return final_recipes

    def invoke_optimization(self):
        """
        initiate the copper model training the
        and store the model

        :return:
        """
        scrap_orders = '../../data/1/scrap_orders.json'
        schedule = '../../data/1/production_schedule.json'
        constraints = '../../data/1/constraints.json'
        scrap_inventory = '../../data/1/scrap_inventory.json'
        final_recipes = self.optimizer(scrap_orders, schedule, constraints, scrap_inventory)
        final_recipes.to_csv('../output/final_recipes.csv', index=False)

        return "Optimization result has been written down to final_recipes.csv"


if __name__ == '__main__':
    reOpt = RecipeOptimizer()
    reOpt.invoke_optimization()
    print("Optimization result has been written down to final_recipes.csv")
