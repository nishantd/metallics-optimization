
class YieldModel(object):
    def __init__(self, data_dir):
        self.data_dir = data_dir

    def create_model(self):
        # Uses the data to create a yield model
        pass

    # In future, the get_estimate function might take a scrap mix and give
    # back the estimated yield. For now, give back the estimate for each
    # scrap type.

    def get_estimates(self):
        # For now, just give back estimates for each scrap type.
        # TODO: Mock for now.
        # Also later may need to give back a distribution.
        return {"bushling":0.9, "pig_iron":0.97, "municipal_shred":0.75, "skulls":0.8}


        
