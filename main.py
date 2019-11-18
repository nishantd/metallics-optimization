import json

from pandas.io.json import json_normalize

from cu_estimator import CuEstimator

with open('data/1/previous_heats_with_properties.json') as f:
    data = json.load(f)
df = json_normalize(data)
df = df.rename(columns=lambda col: col.rpartition('.')[-1])

estimator = CuEstimator()
estimator.fit(df)

row = df.iloc[0]
print(estimator.predict(row))
