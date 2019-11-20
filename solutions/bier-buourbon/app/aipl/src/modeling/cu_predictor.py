import numpy as np


BUSHELING = "bushling"
PIG_IRON = "pig_iron"
SHRED = "municipal_shred"
SKULLS = "skulls"


def get_cu_for_mix(model, steel_grade, busheling, shred, pigiron, skulls):
    """
    Using model and inputs to do prediction

    Parameter: model, pickle file, in which linear regression model is stored
    parameter: steel_grade, string, steel grade
    parameter: busheling, int
    parameter: pigiron, int
    parameter: shred, int
    parameter: skulls, int

    """

    steel_grade_list = ["ST1", "ST2", "ST3"]

    # convert stee_grade string to int
    for idx, item in enumerate(steel_grade_list):
        if item == steel_grade:
            steel_grade = idx + 1

    x_list = [steel_grade, busheling, shred, pigiron, skulls]
    x = np.asarray(x_list)
    result = model.predict(x)

    # to keep sure the result not < 0
    for item in result:
        if item < 0:
            item = 0
    return result


def get_cu_per_scraptype():
    return {BUSHELING: 0.1, PIG_IRON: 0.0, SHRED: 0.2, SKULLS: 0.3}
