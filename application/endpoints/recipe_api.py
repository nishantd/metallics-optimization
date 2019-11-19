from flask import Flask, request, jsonify
import numpy as np
import pickle as p

from application.modelling.copper_training import CopperPredictor
from application.modelling.optimization import RecipeOptimizer
from application.modelling.value_in_use import ValueInUsePredictor
from application.modelling.yield_training import YieldPredictor

app = Flask(__name__)


@app.route("/")
def home():
    return "You reached to the endpoint solution that at the high level might resemble the actual metallics solution in terms of the components. I.e. Models for Copper and yield estimation, the optimizer that creates recipes and uses the pickles (or api's to the pickles) to create recipes, etc.!"


@app.route('/api/', methods=['POST'])
def make_calc():
    data = request.get_json()
    prediction = np.array2string(model.predict(data))
    b = jsonify(prediction)
    return jsonify(prediction)


@app.route('/api/train/cu/', methods=['GET'])
def train_cu():
    cup = CopperPredictor();
    response = cup.invoke_copper_training()
    return jsonify(response)


@app.route('/api/train/yield/', methods=['GET'])
def train_yield():
    yp = YieldPredictor();
    response = yp.invoke_yield_training()
    return jsonify(response)


@app.route('/api/get/value-in-use/', methods=['GET'])
def get_value_in_use():
    sample = {"bushling": 300, "pig_iron": 200, "municipal_shred": 350, "skulls": 200}
    value_in_use = ValueInUsePredictor(sample)
    response = value_in_use.get_value_in_use_training()
    return response.to_json()


@app.route('/api/recipe/optimization/start/', methods=['GET'])
def startRecipeOptimization():
    recOpt = RecipeOptimizer()
    response = recOpt.invoke_optimization()
    return jsonify(response)


if __name__ == '__main__':
    modelfile = '../pickles/recipe_model.pickle'
    model = p.load(open(modelfile, 'rb'))
    app.run(debug=True, host='0.0.0.0')