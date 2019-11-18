import json
import sys, os

class RecipeOptimizer(object):
    def __init__(self, data_dir, copper_model, yield_model):
        self.data_dir = data_dir
        self.copper_model = copper_model
        self.yield_model = yield_model

    def initialize(self):
        # Uses the data to initialize if required.
        pass

    def create_recipes_for_schedule(self):
        # TODO: Mock for now.
        s = None
        with open(os.path.dirname(self.data_dir.rsplit('/', 1)[0]) + '/final_output_example.json') as f:
            s = f.read()
        schedule_recipes = json.loads(s)
        return schedule_recipes




        
