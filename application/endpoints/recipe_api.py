from flask import Flask, request, redirect, url_for, flash, jsonify
import numpy as np
import pickle as p

app = Flask(__name__)

@app.route("/")
def home():
    return "You reached to the endpoint solution that at the high level might resemble the actual metallics solution in terms of the components. I.e. Models for Copper and yield estimation, the optimizer that creates recipes and uses the models (or api's to the models) to create recipes, etc.!"

@app.route('/api/', methods=['POST'])
def makecalc():
    data = request.get_json()
    prediction = np.array2string(model.predict(data))
    b = jsonify(prediction)
    return jsonify(prediction)

if __name__ == '__main__':
    modelfile = '../models/recipe_model.pickle'
    model = p.load(open(modelfile, 'rb'))
    app.run(debug=True, host='0.0.0.0')