import pandas as pd
import pickle
from sklearn.linear_model import LinearRegression
import json


class CopperPredictor:
    def __init__(self):
        # model id - (every model should get a property model_id)
        self.commodities = ['bushling', 'pig_iron', 'municipal_shred', 'skulls']
        self.training_data = '../../data/1/previous_heats_with_properties.json'

    def _copper_model(self, training_data):
        """
        yield_estimation: This function trains the copper estimation model
        split into test/train

        input: training dataframe
        output: fit model
        """

        model = LinearRegression()
        model = model.fit(training_data[[c+'_norm' for c in self.commodities]], training_data['cu_pct'])

        return model

    def _normalize_commodities(self, training_data):
        """
        normalize_commodities: normalize the commodities so we are training on percentage of commodity

        input: training dataframe
        output: training dataframe with the commodities normalized
        """
        for c in self.commodities:
            training_data[c+'_norm'] = training_data[c]/training_data[self.commodities].sum(axis=1)

        return training_data

    def _load_training_data(self, training_data):
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
            for c in self.commodities:
                training.loc[i, c] = training.loc[i, 'actual_recipe'][c]
                training.loc[i, c] = training.loc[i, 'actual_recipe'][c]
                training.loc[i, c] = training.loc[i, 'actual_recipe'][c]
                training.loc[i, c] = training.loc[i, 'actual_recipe'][c]
            training.loc[i, 'cu_pct'] = training.loc[i, 'chemistry']['cu_pct']
        training = self._normalize_commodities(training)

        return training

    def _run_training(self, training_data):
        """
        run_training: train the model using the training dataset

        TODO: Split for train/test and score model (data was too small for this so only training metrics available)

        input:
        None
        output:
        linear model
        """

        data = self._load_training_data(training_data)
        model = self._copper_model(data)
        self._save_model(model)

    def _save_model(self, model):
        """
        save_model: save the model as a pickle file

        input: fitted model
        output: saved pickle file
        """

        pickle_out = open("../pickles/copper_model.pickle","wb")
        pickle.dump(model, pickle_out)
        pickle_out.close()

        return
    def invoke_copper_training(self):
        """
        initiate the copper model training the
        and store the model

        :return:
        """
        import time
        start_time = time.time()
        self._run_training(self.training_data)
        return "Copper model execution completed in "+"{0:.2f}".format(time.time() - start_time)+" seconds."


if __name__ == '__main__':
    """ Still Need To Account For Heel"""
    cu = CopperPredictor()
    cu.invoke_copper_training()
    print("CopperPredictor training complete")