from flask import Flask, request, jsonify
import numpy as np
import pickle as p

from application.modelling.copper_training import CopperPredictor

app = Flask(__name__)

@app.route("/")
def home():
    return "You reached to the endpoint solution that at the high level might resemble the actual metallics solution in terms of the components. I.e. Models for Copper and yield estimation, the optimizer that creates recipes and uses the pickles (or api's to the pickles) to create recipes, etc.!"

@app.route('/api/', methods=['POST'])
def makecalc():
    data = request.get_json()
    prediction = np.array2string(model.predict(data))
    b = jsonify(prediction)
    return jsonify(prediction)

@app.route('/api/train/cu/', methods=['GET'])
def trainCu():
    cuP = CopperPredictor();
    response = cuP.invoke_copper_training()
    return jsonify(response)

if __name__ == '__main__':
    modelfile = '../pickles/recipe_model.pickle'
    model = p.load(open(modelfile, 'rb'))
    app.run(debug=True, host='0.0.0.0')