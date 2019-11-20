# Any preprocessing on the ingested data


import json
import pandas as pd
from sklearn.utils import shuffle
from statsmodels.iolib.smpickle import load_pickle
import numpy as np
import statsmodels.api as sm


# from ..modeling.yield_modeling import yield_build_model
# from ..modeling.yield_predictor import get_yileld_for_mix

# from ..modeling.cu_modeling import cu_build_model

# Load pandas dataframe from json

def import_json_file(file_name, folder_name):
    """
    load json file as dataframe
    
    parameter: file_name, string
    parameter: folder_name, string
    """
    data_path = f'../../../../data/{folder_name}/{file_name}'
    with open(data_path, 'r') as datafile:
        data = json.load(datafile)
    df = pd.DataFrame(data)
    return df


def dataframe(df, col_name):
    """
    Convert dictionaries in columns to dataframe
    
    parameter: df, dataframe which conraions dictionaroes in the clomun.
    parameter: col_name, list, which contains dictionaries
    
    """
    length = len(col_name)
    for i in range(length):
        ls = list(df[col_name[i]])
        df_new = pd.DataFrame.from_dict(ls)
        df.drop(columns=[col_name[i]], inplace=True)
        df = pd.concat([df, df_new], axis=1)
    return df


def replace_string(df, col_name):
    """
    Using number to replace string data in df 
    parameter: df, dataframe, data
    parameter: col_name, list, which contations string
    """
    unique_steel_grade = df[col_name].unique()
    length = len(unique_steel_grade)
    for i in range(length):
        df.replace(unique_steel_grade[i], (i + 1), inplace=True)
    return df


def preprocess_data(drop_col):
    """
    load data, drop useless columns, replace string witn numbers
    """
    df = import_json_file('previous_heats_with_properties.json', 1)
    df = dataframe(df, ['actual_recipe', 'chemistry'])

    df.drop(columns=drop_col, inplace=True)
    #df = replace_string(df, 'steel_grade')
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
    x_test = x[num:]
    y_test = y[num:]

    return x_train, y_train, x_test, y_test


def get_cu_for_mix(model, busheling, shred, pigiron, skulls):
    """
    Using model and inputs to do prediction

    Parameter: model, pickle file, in which linear regression model is stored
    parameter: steel_grade, string, steel grade
    parameter: busheling, int
    parameter: pigiron, int
    parameter: shred, int
    parameter: skulls, int

    """

    x_list = [busheling, shred, pigiron, skulls]
    x = np.asarray(x_list)
    result = model.predict(x)

    # to keep sure the result not < 0
    for item in result:
        if item < 0:
            item = 0
    return result


def cu_build_model(x, y):
    """
    Train linear regression model and save model

    parameter: x, numpy array, training data x
    parameter: y, numpy array, training data y
    """
    model = sm.OLS(y, x).fit()
    model.save('cu_model.pickle')


def yield_build_model(x, y):
    model = sm.OLS(y, x).fit()
    model.save('yield_model.pickle')


def get_yileld_for_mix(model, busheling, shred, pigiron, skulls):
    """
      Using model and inputs to do prediction

        Parameter: model, pickle file, in which linear regression model is stored
         Parameter: required_weight, int
        parameter: steel_grade, string
        parameter: busheling, int
        parameter: pigiron, int
        parameter: shred, int
        parameter: skulls, int
    """

    # convert stee_grade string to int

    x_list = [busheling, shred, pigiron, skulls]
    x = np.asarray(x_list)
    result = model.predict(x)

    # to keep sure the result not < 0
    for item in result:
        if item < 0:
            item = 0
    return result


df = preprocess_data(
    drop_col=['heat_id', 'heat_seq', 'required_weight', 'tap_weight', 'steel_grade'])

x_train, y_train, x_test, y_test = training_and_testing_data(df, 0.8, 'cu_pct')

# build model
cu_build_model(x_train, y_train)
cu_model_name = 'cu_model.pickle'
model_cu = load_pickle(cu_model_name)
# do prediction

#example
busheling = 200
shred = 300
pigiron = 0
skulls = 200

cu_results = get_cu_for_mix(model_cu, busheling, shred, pigiron, skulls)

print(f"CU results: {cu_results}")

# yield
df = preprocess_data(drop_col=['heat_id', 'heat_seq', 'cu_pct', 'steel_grade', 'required_weight'])
x_train, y_train, x_test, y_test = training_and_testing_data(df, 0.8, 'tap_weight')
#build model
yield_model_name = 'yield_model.pickle'
yield_build_model(x_train, y_train)
model = load_pickle(yield_model_name)
# do prediction
yield_result = get_yileld_for_mix(model, busheling, shred, pigiron, skulls)

print(f"yield results: {yield_result}")