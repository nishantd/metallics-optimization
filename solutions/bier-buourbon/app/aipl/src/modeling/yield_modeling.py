# Train a yield_prediction model

import statsmodels.api as sm

    
def yield_build_model(x, y):
    model = sm.OLS(y, x).fit()
    model.save('yield_model.pickle')

