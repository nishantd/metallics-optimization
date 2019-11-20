# Train a cu_prediction model
import statsmodels.api as sm

def cu_build_model(x,y):
    
    """
    Train linear regression model and save model
    
    parameter: x, numpy array, training data x
    parameter: y, numpy array, training data y
    """
    model = sm.OLS(y, x).fit()
    model.save('cu_model.pickle')
    





