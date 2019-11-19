import glob
import os
from asciimatics.renderers import FigletText, Fire
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.effects import Print
from asciimatics.exceptions import ResizeScreenError
import argparse
import pandas as pd
import json
import numpy as np
import tqdm

import matplotlib.pylab as plt


def flames_cpu_screen(screen):
    scenes = []

    effects = [
        Print(screen,
              Fire(screen.height, 80, "*" * 70, 0.8, 60, screen.colours,
                   bg=screen.colours >= 256),
              0,
              speed=1,
              transparent=False),
        Print(screen,
              FigletText("OMG!", "banner3"),
              (screen.height - 4) // 2,
              colour=Screen.COLOUR_BLACK,
              speed=1,
              stop_frame=30),
        Print(screen,
              FigletText("THE CPU", "banner3"),
              (screen.height - 4) // 2,
              colour=Screen.COLOUR_BLACK,
              speed=1,
              start_frame=30,
              stop_frame=50),
        Print(screen,
              FigletText("IS", "banner3"),
              (screen.height - 4) // 2,
              colour=Screen.COLOUR_BLACK,
              speed=1,
              start_frame=50,
              stop_frame=70),
        Print(screen,
              FigletText("ON FIRE!", "banner3"),
              (screen.height - 4) // 2,
              colour=Screen.COLOUR_BLACK,
              speed=1,
              start_frame=70),
    ]
    scenes.append(Scene(effects, 100))
    screen.play(scenes, stop_on_resize=True, repeat=False)


def print_flames():
    try:
        Screen.wrapper(flames_cpu_screen)
    except ResizeScreenError:
        pass


def load_data(path):
    res = {}
    for f in glob.glob(path):
        with open(f, "r") as fh:
            res[os.path.basename(f).replace(".json", "")] = pd.DataFrame(json.load(fh))

    df_prod = res["production_schedule"]
    df_prod["cu_pct"] = df_prod["chemistry"].apply(lambda x: x['cu_pct'])
    df_prod.drop("chemistry", axis=1, inplace=True)

    df_chem = res["previous_heats_with_properties"]
    df_chem["cu_pct"] = df_chem["chemistry"].apply(lambda x: x['cu_pct'])
    for b in ["bushling", "pig_iron", 'municipal_shred', 'skulls']:
        df_chem[b] = df_chem["actual_recipe"].apply(lambda x: x[b])

    df_chem["total_input"] = df_chem[["bushling", "pig_iron", 'municipal_shred', 'skulls']].sum(
        axis=1)
    for b in ["bushling", "pig_iron", 'municipal_shred', 'skulls']:
        df_chem[b] /= df_chem["total_input"]

    df_chem["yield"] = df_chem["tap_weight"] / df_chem["total_input"]

    df_chem.drop("chemistry", axis=1, inplace=True)
    df_chem.drop("actual_recipe", axis=1, inplace=True)

    df_order = res['scrap_orders']

    df_constr = res['constraints']
    df_constr = pd.DataFrame(map(lambda x: x[0], df_constr.values.tolist()))

    df_inven = res['scrap_inventory']

    return df_prod, df_chem, df_order, df_constr, df_inven


# todo: consider yield
def generate_schedule_random(commodities, schedule, df_constr, iterations=10000):
    """
    generates a schedule by brute force
    """
    df_constr = df_constr.set_index("name")
    df_constr = df_constr.reindex([c["name"] for c in commodities])
    df_constr["min"] = df_constr["min"].fillna(0)
    df_constr["max"] = df_constr["max"].fillna(np.inf)

    r_min = df_constr["min"].values
    r_max = df_constr["max"].values

    c_cu = np.array(np.array([c["cu"] for c in commodities]))
    s_cu = np.array(np.array([s["cu"] for s in schedule]))
    s_weight = np.array([s["weight"] for s in schedule])
    c_inv = np.array([c["inventory"] for c in commodities])
    c_price = np.array([c["price"] for c in commodities])

    cost = [np.inf]
    cu_predicted = None
    res = None
    miss_chem, miss_inven, miss_constr = 0, 0, 0
    valid = 0

    for _ in tqdm.tqdm(range(iterations)):

        bad = False

        # generate schedule
        res_t = []
        for s in [s["weight"] for s in schedule]:
            res_t.append(np.random.random_integers(0, s, size=len(commodities)))
        res_t = np.vstack(res_t)

        # make weights equal to schedule weights by fixing last commodity
        res_t[:, -1] = s_weight - res_t[:, :-1].sum(axis=1)

        # check chemistry
        cu_predicted_t = res_t.dot(c_cu.transpose()) / s_weight
        if not (cu_predicted_t <= s_cu).all():
            miss_chem += 1
            bad = True

        # check inventory
        used = res_t.sum(axis=0)
        if not (used <= c_inv).all():
            miss_inven += 1
            bad = True

        # check side constraints
        if (res_t < r_min).any() or (res_t > r_max).any():
            miss_constr += 1
            bad = True

        if bad:
            cost += [cost[-1]]
            continue

        valid += 1
        cost_temp = np.sum(used * c_price)

        # check if costs are lower than best so far
        if cost_temp < cost[-1]:
            res = res_t
            cu_predicted = cu_predicted_t
            cost += [cost_temp]

    stats = pd.Series({"iterations": iterations,
                       "miss_chem": miss_chem, "miss_inven": miss_inven, "miss_constr": miss_constr,
                       "valid": valid,
                       "lowest_cost": cost[-1]})
    return res, stats, cost, cu_predicted


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str)
    args = parser.parse_args()

    # validate input
    assert os.path.isdir(args.path), f"{args.path} is not a valid directory, abort"

    path_json = args.path + "*.json"
    assert len(list(glob.glob(path_json))) > 0, \
        "Could not find any jsons under {args.path}, did you enter the right path?"

    # load data
    df_prod, df_chem, df_order, df_constr, df_inven = load_data(path_json)
    print(df_prod)
    print(df_chem)
    print(df_order)
    print(df_constr)
    print(df_inven)

    # scrap quality estimation
    

    # Optimizing of the schedule
    commodities = [{"name": "A", "price": 10, "cu": 0.01, "inventory": 1000, "yield": 0.99},
                   {"name": "B", "price": 20, "cu": 0.05, "inventory": 1000, "yield": 0.95}],

    schedule = df_prod[["cu_pct", "required_weight"]].rename(
        columns={"cu_pct": "cu", "required_weight": "weight"}).to_dict(orient='record')

    constraints = df_constr.pivot(index="scrap_type", columns="type", values="weight")
    constraints = constraints.rename(columns={"minimum": "min", "maximum": "max"})

    # print_flames()
    res, stats, cost, cu_predicted = \
        generate_schedule_random(commodities, schedule, constraints, iterations=50000)

    print(res)

    # [
    #     {"heat_seq": 61, "heat_id": "heat-601", "steel_grade": "ST1", "predicted_tap_weight": 1000,
    #      "predicted_chemistry": {"cu_pct": 0.095},
    #      "suggested_recipe": {"bushling": 300, "pig_iron": 200, "municipal_shred": 350,
    #                           "skulls": 200}},
    #     {"heat_seq": 62, "heat_id": "heat-602", "steel_grade": "ST1", "predicted_tap_weight": 1100,
    #      "predicted_chemistry": {"cu_pct": 0.1},
    #      "suggested_recipe": {"bushling": 250, "pig_iron": 200, "municipal_shred": 300,
    #                           "skulls": 250}}
    # ]
