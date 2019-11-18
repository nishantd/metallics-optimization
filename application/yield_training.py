import pandas as pd
import pickle
from sklearn.linear_model import LinearRegression()

def yield_model(data):
    """
    yield_estimation: This function trains the yield estimation model
    
    """
    return model

def load_training_data():
    """
    load_training_data:
    """
    return data

def run_training():
    """
    run_training:
    """
    data = load_training_data()
    model = yield_model(data)

def save_model(model):
    """
    save_model: 
    """
    pickle_out = open("models/yield_model.pickle","wb")
    pickle.dump(model, pickle_out)
    pickle_out.close()

if __name__ == '__main__':
    model = run_training()
    save_model(model)
    print("training complete")