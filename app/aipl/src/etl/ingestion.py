# Load pandas dataframe from json

import pandas as pd
import json


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
    for i in range (length):
        ls = list(df[col_name[i]])
        df_new = pd.DataFrame.from_dict(ls)
        df.drop(columns=[col_name[i]], inplace=True)
        df = pd.concat([df, df_new], axis=1)
    return df


