import pandas as pd
import pickle
from sklearn.linear_model import LinearRegression
import json

commodities = ['bushling', 'pig_iron', 'municipal_shred', 'skulls']
training_data = '../data/1/previous_heats_with_properties.json'

def copper_model(training_data):
    """
    yield_estimation: This function trains the copper estimation model
    split into test/train
    
    input: training dataframe
    output: fit model
    """
    
    model = LinearRegression()
    model = model.fit(training_data[[c+'_norm' for c in commodities]], training_data['cu_pct'])

    return model

def normalize_commodities(training_data):
    """
    normalize_commodities: normalize the commodities so we are training on percentage of commodity
    
    input: training dataframe
    output: training dataframe with the commodities normalized 
    """
    for c in commodities:
        training_data[c+'_norm'] = training_data[c]/training_data[commodities].sum(axis=1)
        
    return training_data

def load_training_data(training_data):
    """
    load_training_data: load the training dataset into a dataframe
    
    TODO: Parameterize the location of the training data, the set commodities
    
    input: training set location
    output: dataframe with training data, xnames, and ynames
    """

    with open(training_data) as json_file:
        training = json.load(json_file)
    training = pd.read_json(training_data)
    for i, row in training.iterrows():
        for c in commodities:
            training.loc[i, c] = training.loc[i, 'actual_recipe'][c]
            training.loc[i, c] = training.loc[i, 'actual_recipe'][c]
            training.loc[i, c] = training.loc[i, 'actual_recipe'][c]
            training.loc[i, c] = training.loc[i, 'actual_recipe'][c]
        training.loc[i, 'cu_pct'] = training.loc[i, 'chemistry']['cu_pct']
    training = normalize_commodities(training)
    
    return training

def run_training(training_data):
    """
    run_training: train the model using the training dataset
    
    TODO: Split for train/test and score model (data was too small for this so only training metrics available)
    
    input:
    None
    output:
    linear model
    """
    
    data = load_training_data(training_data)
    model = copper_model(data)
    
    return model

def save_model(model):
    """
    save_model: save the model as a pickle file
    
    input: fitted model
    output: saved pickle file 
    """
    
    pickle_out = open("models/copper_model.pickle","wb")
    pickle.dump(model, pickle_out)
    pickle_out.close()
    
    return

if __name__ == '__main__':
    """ Still Need To Account For Heel"""
    model = run_training(training_data)
    save_model(model)
    print("training complete")