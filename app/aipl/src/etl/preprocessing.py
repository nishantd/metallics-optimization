# Any preprocessing on the ingested data

from ingestion import import_json_file as ijf 
from ingestion import dataframe 
import pandas as pd
from sklearn.utils import shuffle
from statsmodels.iolib.smpickle import load_pickle

from modeling.cu_modeling import cu_build_model
from modeling.cu_predictor import get_cu_for_mix 

from modeling.yield_modeling import yield_build_model
from modeling.yield_predictor import get_yileld_for_mix





def replace_string(df, col_name):
    """
    Using number to replace string data in df 
    parameter: df, dataframe, data
    parameter: col_name, list, which contations string
    """
    unique_steel_grade = df[col_name].unique()
    length = len(unique_steel_grade)
    for i in range (length):
        df.replace(unique_steel_grade[i], (i+1), inplace=True)
    return df

def preprocess_data(drop_col):
    """
    load data, drop useless columns, replace string witn numbers
    """
    df = ijf('previous_heats_with_properties.json', 1)
    df = dataframe(df, ['actual_recipe', 'chemistry'])

    df.drop(columns=drop_col, inplace=True)
    df = replace_string(df, 'steel_grade')
    return df

def training_and_testing_data(df, pct, y_col_name):
    """
    set training data
    parameter: df, dataframe, data
    parameter: pct, float, how much data will be used as training data
    """
    df = shuffle(df)
    
    df_y = df[y_col_name]
    df.drop(columns=[y_col_name], inplace=True)
    print(df)
    
    
    x = df.to_numpy()
    print(x)
    y = df_y.to_numpy()
    
    num = int(len(y) * pct)
    
    # training data
    x_train = x[::]
    y_train = y[::]
    
    # testing data
    x_test = x[num :]
    y_test = y[num :]
    
    return x_train, y_train, x_test, y_test






    
# copper
df = preprocess_data(drop_col=['heat_id', 'heat_seq', 'required_weight', 'tap_weight'])
x_train, y_train, x_test, y_test = training_and_testing_data(df, 0.8, 'cu_pct')

# build model
cu_build_model(x_train, y_train)
cu_model_name = 'cu_model.pickle'
model_cu = load_pickle(cu_model_name)
# do prediction
cu_results = get_cu_for_mix(model_cu, steel_grade, busheling, shred, pigiron, skulls)



# yield
df = preprocess_data(drop_col=['heat_id', 'heat_seq', 'cu_pct'])
x_train, y_train, x_test, y_test = training_and_testing_data(df, 0.8, 'tap_weight')
# build model
yield_model_name = 'yield_model.pickle'
yield_build_model(x_train, y_train, yield_model_name)
model = load_pickle(yield_model_name)
#do prediction
yield_result = get_yileld_for_mix(required_weight, steel_grade, busheling, shred, pigiron, skulls)
