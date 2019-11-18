import json
import sys, os

class RecipeOptimizer(object):
    def __init__(self, data_dir, copper_model, yield_model, cost_estimator):
        self.data_dir = data_dir
        self.copper_model = copper_model
        self.yield_model = yield_model
        self.cost_estimator = cost_estimator

    def initialize(self):
        # Uses the data to initialize if required.
        pass

    def create_recipes_for_schedule(self):
        # TODO: Mock for now.
        # Just return back the example final output.
        s = None
        #with open(os.path.join(self.data_dir.rsplit('/', 1)[0], '/final_output_example.json')) as f:
        # TODO: fix above
        with open('data/final_output_example.json') as f:
            s = f.read()
        schedule_recipes = json.loads(s)
        return schedule_recipes




        
