import statistics
import math


# takes in two set data where all the data are corresponding, which implies that the len of the two set of the data are same
def nse(sim, ob):
    ob_mean = statistics.mean(ob)
    upper = 0.0
    lower = 0.0
    try:
        for count, val in enumerate(sim):
            if math.isnan(ob[count]) or ob[count] is None or ob[count] == 999 or ob[count] == 0 or  ob[count] == -9999.9:
                continue
            if math.isnan(val):
                val = 0
            upper = (ob[count] - val) ** 2 + upper
            lower = (ob[count] - ob_mean) ** 2 + lower
    except Exception as e:
        print(e)
        print(upper)
        print(lower)
    res = 1 - (upper / lower)
    return res


# takes in two set of dict, where data are not corresponding, needs to find the corresponding data from the other dict to calculate the correct nse
def nse_with_dates(sim, ob):
    ob_mean = statistics.mean(ob.values())
    upper = 0.0
    lower = 0.0
    try:
        for val in ob:
            if val in list(sim.keys()):
                ob_val = ob[val]
                val = sim[val]
                if math.isnan(ob_val) or ob_val is None or \
                        ob_val == 999 or ob_val == 0 or ob_val == -9999.9:
                    continue
                if math.isnan(val):
                    continue
                upper = (ob_val - val) ** 2 + upper
                lower = (ob_val - ob_mean) ** 2 + lower
    except Exception as e:
        print(e)
    res = 1 - (upper / lower)
    return res


def ioa_with_dates(ob, sim):
    ob_mean = statistics.mean(ob)
    upper = 0.0
    lower = 0.0
    try:
        for val in ob:
            if val in list(sim.keys()):
                ob_val = ob[val]
                if ob_val is None or ob_val == 999 or ob_val == 0 or  ob_val == -9999.9:
                    continue
                if math.isnan(sim[val]):
                    continue
                upper = (ob_val - sim[val]) ** 2 + upper
                lower = (abs(sim[val] - ob_mean) + abs(ob_val - ob_mean)) ** 2 + lower
    except Exception as e:
        print(e)
    res = 1 - (upper / lower)
    return res


def rmsd_with_dates(ob, sim):
    n = 0
    upper = 0
    try:
        for val in ob:
            if val in list(sim.keys()):
                ob_val = ob[val]
                if ob_val is None or ob_val == 999 or ob_val == 0 or  ob_val == -9999.9:
                    continue
                if math.isnan(sim[val]):
                    continue
                dif = (sim[val] - ob[val]) ** 2
                upper = upper + dif
                n = n + 1
    except Exception as e:
        print(e)

    return math.sqrt((upper / n))


def r_square(ob, sim):
    ob_mean = statistics.mean(ob)
    upper = 0.0
    lower = 0.0
    try:
        for val in ob:
            if val in list(sim.keys()):
                ob_val = ob[val]
                if ob_val is None or ob_val == 999 or ob_val == 0 or  ob_val == -9999.9:
                    continue
                if math.isnan(sim[val]):
                    continue
                upper = (ob_val - sim[val]) ** 2 + upper
                lower = (ob_val - ob_mean) ** 2 + lower
    except Exception as e:
        print(e)
    res = 1 - (upper / lower)
    return res


def MBE(sim, ob):
    dif = 0
    count = 0
    try:
        for val in sim:
            sim_value = sim[val]
            ob_value = ob[val]
            if math.isnan(ob_value) or ob_value is None or ob_value == 999 or ob_value == 0 or ob_value == -9999.9:
                continue
            if math.isnan(sim_value):
                continue
            dif = sim_value - ob_value + dif
            count = count + 1
    except Exception as e:
        print(e)
    res = dif / count
    return res
