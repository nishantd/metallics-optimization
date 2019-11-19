from asciimatics.particles import PalmFirework, StarFirework, RingFirework, SerpentFirework
from asciimatics.renderers import Fire, SpeechBubble
from asciimatics.effects import Print, Stars
import argparse
import numpy as np
import tqdm
from random import randint, choice
from asciimatics.effects import RandomNoise
from asciimatics.renderers import FigletText, Rainbow
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError
import pandas as pd
import json
import glob
import os
import numpy
from sklearn.linear_model import Lasso
import matplotlib.pylab as plt


def print_intro():
    def demo(screen):
        effects = [
            RandomNoise(screen,
                        signal=Rainbow(screen,
                                       FigletText("TEAM DROP TABLES")))
        ]
        screen.play([Scene(effects, 0)], stop_on_resize=True, repeat=False)

    try:
        Screen.wrapper(demo)
    except ResizeScreenError:
        pass


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


def fireworks(screen):
    scenes = []
    effects = [
        Stars(screen, screen.width),
        Print(screen,
              SpeechBubble("Press space to see it again"),
              y=screen.height - 3,
              start_frame=300)
    ]
    for _ in range(20):
        fireworks = [
            (PalmFirework, 25, 30),
            (PalmFirework, 25, 30),
            (StarFirework, 25, 35),
            (StarFirework, 25, 35),
            (StarFirework, 25, 35),
            (RingFirework, 20, 30),
            (SerpentFirework, 30, 35),
        ]
        firework, start, stop = choice(fireworks)
        effects.insert(
            1,
            firework(screen,
                     randint(0, screen.width),
                     randint(screen.height // 8, screen.height * 3 // 4),
                     randint(start, stop),
                     start_frame=randint(0, 250)))

    effects.append(Print(screen,
                         Rainbow(screen, FigletText("CONGRATULATIONS")),
                         screen.height // 2 - 6,
                         speed=1,
                         start_frame=100))
    effects.append(Print(screen,
                         Rainbow(screen, FigletText("TO YOUR")),
                         screen.height // 2 + 1,
                         speed=1,
                         start_frame=100))
    effects.append(Print(screen,
                         Rainbow(screen, FigletText("OPTIMAL SCHEDULE")),
                         screen.height // 2 + 1,
                         speed=1,
                         start_frame=100))
    scenes.append(Scene(effects, -1))

    screen.play(scenes, stop_on_resize=True, repeat=False)


def print_fireworks():
    while True:
        try:
            Screen.wrapper(fireworks)
        except ResizeScreenError:
            pass


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


def generate_schedule_random(commodities, schedule, df_constr, iterations, verbose=True):
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
    random_p = True
    random_matrix = True
    res_t = None

    for _ in tqdm.tqdm(range(iterations), disable=not verbose):

        bad = False

        if random_p:
            p = np.random.uniform(0, 1, len(commodities))

        if random_matrix:
            res_t = []

            for s in [s["weight"] for s in schedule]:
                x = np.random.binomial(s, p, size=len(commodities))
                x = np.maximum(x, r_min)
                x = np.minimum(x, r_max)
                res_t.append(x)

            res_t = np.vstack(res_t)
        else:
            res_t = res_t + (np.random.binomial(2, 0.5, size=res_t.shape) - 1.0)
            res_t = np.maximum(res_t, r_min)
            res_t = np.minimum(res_t, r_max)

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
            random_p = True
            random_matrix = True
            continue

        valid += 1
        cost_temp = np.sum(used * c_price)
        random_p = choice([False] * 19 + [True])
        random_matrix = choice([False] * 19 + [True])

        # check if costs are lower than best so far
        if cost_temp < cost[-1]:
            res = res_t
            cu_predicted = cu_predicted_t
            cost += [cost_temp]

    if valid == 0:
        print("WARNING: Did not even found one valid schedule by brute force....")

    stats = pd.DataFrame({"iterations": iterations,
                          "miss_chem": miss_chem, "miss_inven": miss_inven,
                          "miss_constr": miss_constr,
                          "valid": valid, "lowest_cost": cost[-1]}, index=[0])
    return res, stats, cost, cu_predicted


def scrap_quality_estimation(df_chem, df_order, df_inven, price_agg="avg"):
    """ This function will estimate the quality of the scrap by estimating the portion of copper and
    yield in the scrap component

    :param df_chem: dataframe containing the chemical component of the scrap
    :param df_order: dataframe contaning the order history with the price of the scrape
    :param: df_inven: dataframe contaning the inventory storage of the scrape
    :param: price_aggregate: price aggregation ("avg" or "last")
    :return: results_df : dataframe with Component, cu_pct, price_per_ton, yield, inv_weight
    """
    names_commodities = list(set(df_order["scrap_type"]) & set(df_inven["scrap_type"]))
    names_commodities.sort()

    # the portion of the total evaporated material
    lost_portion = 1 - df_chem["yield"].values

    # the portion of the evaporated material in every scrap material
    the_component_por = df_chem[names_commodities].values

    lost_share_per_component = Lasso(alpha=0.00001, fit_intercept=False, precompute=True,
                                     positive=True, max_iter=10000)
    lost_share_per_component.fit(the_component_por, lost_portion)

    # portion of yield in every component
    yield_coef = 1 - lost_share_per_component.coef_
    yield_ = df_chem[names_commodities].values * yield_coef

    # total copper portion in the whole scrap
    total_copper_port = df_chem["cu_pct"].values

    # copper portion in every component
    copper_port = Lasso(alpha=0.00001, fit_intercept=False, precompute=True, positive=True,
                        max_iter=10000)
    copper_port.fit(yield_, total_copper_port)
    copperport = copper_port.coef_

    price_per_ton = numpy.zeros(len(names_commodities))
    ind = 0

    # calculate the av price per ton payed for the scrap in the inv
    for component in names_commodities:
        if price_agg == "avg":
            df = df_order[df_order['scrap_type'] == component][['weight', 'price_per_ton']]
            p = df['price_per_ton'].values
            w = df['weight'].values
            price_per_ton[ind] = sum(p * w) / sum(w)
        elif price_agg == "last":
            price_per_ton[ind] = df_order[df_order['scrap_type'] == component].sort_values(
                by="order_date")["price_per_ton"].iloc[-1]
        ind = ind + 1

    inv_weight = df_inven['weight'].values
    results_df = pd.DataFrame({'name': names_commodities,
                               'cu': copperport,
                               'price': price_per_ton,
                               'yield': yield_coef,
                               'inventory': inv_weight})
    return results_df


if __name__ == "__main__":

    parser = argparse.ArgumentParser(conflict_handler='resolve')
    parser.add_argument("path", type=str)
    parser.add_argument("--ux", required=False, action="store_true",
                        help="next level user interface")
    parser.add_argument("--last_price", required=False, action="store_true",
                        help="use last price instead of average price")
    parser.add_argument('-v', '--verbose', action="store_true", default=False)
    parser.add_argument("--verbose", required=False, action="store_true",
                        help="print more information!")
    parser.add_argument("--plot", required=False, action="store_true",
                        help="plot the costs")
    args = parser.parse_args()

    # validate input
    assert os.path.isdir(args.path), f"{args.path} is not a valid directory, abort"

    path_json = args.path + "*.json"
    assert len(list(glob.glob(path_json))) > 0, \
        "Could not find any jsons under {args.path}, did you enter the right path?"

    if args.ux:
        args.verbose = True
        print_intro()

    # load data
    df_prod, df_chem, df_order, df_constr, df_inven = load_data(path_json)

    # scrap quality estimation
    df_com = scrap_quality_estimation(df_chem, df_order, df_inven,
                                      price_agg="last" if args.last_price else "avg")
    if args.verbose:
        print("#" * 20 + " Scrap quality estimator" + "#" * 40)
        print(df_com)
        print("#" * 84)

    commodities = df_com.to_dict(orient='record')

    schedule = df_prod[["cu_pct", "required_weight"]].rename(
        columns={"cu_pct": "cu", "required_weight": "weight"}).to_dict(orient='record')

    constraints = df_constr.pivot(index="scrap_type", columns="type", values="weight")
    constraints.reset_index(drop=False, inplace=True)
    constraints = constraints.rename(
        columns={"scrap_type": "name", "minimum": "min", "maximum": "max"}
    )

    if args.ux:
        print_flames()

    res, stats, cost, cu_predicted = \
        generate_schedule_random(commodities, schedule, constraints, iterations=200000,
                                 verbose=args.verbose)

    if args.plot:
        plt.plot([c/res.sum().sum() for c in cost])
        plt.title("Cost for ton of that schedule over brute force iteration")
        plt.xlabel("Brute force iteration")
        plt.ylabel("Average cost of a ton for the optimized schedule")
        plt.gca().set_xlim(left=0)
        plt.show()

    if args.verbose:
        print("#" * 20 + " Schedule optimization stats" + "#" * 37)
        print(stats)
        print("#" * 84)

    if args.ux:
        print_fireworks()

    if res is not None:
        # the output to write in the json file
        print('[')
        for i in range(len(res)):
            prod_header = df_prod.keys()
            print('{"'+prod_header[0]+'":'+str(df_prod[prod_header[0]][i])+', "'+prod_header[1]+\
                  '": "'+str(df_prod[prod_header[1]][i])+'", "'+prod_header[2]+'": "'+str(df_prod[prod_header[2]][i])+\
                  '", "predicted_tap_weight": '+str(df_prod[prod_header[3]][i])+', '+'"predicted_chemistry": {"cu_pct": '\
                  +str(cu_predicted[i])+'}, "suggested_recipe": {"bushling": '+str(res[i][0])+\
                  ', "pig_iron": '+str(res[i][1])+', "municipal_shred": '\
                  +str(res[i][2])+', '+'"skulls": '+str(res[i][3])+'}},')

        print(']')
