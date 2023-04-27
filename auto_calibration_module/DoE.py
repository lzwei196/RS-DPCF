##generate the sample points first through sobol sequence
import torch
import numpy
from numpy import ndarray
import numpy as np

def sobol(dimension, draw, seed=None):
    soboleng = torch.quasirandom.SobolEngine(dimension=dimension)
    n = numpy.array(soboleng.draw(draw))
    return n

# return ranomized soil sample points
# the number of var indicate how many variables there are
# the number of sets indicate how many pairs of varibales are needed
# var range takes in a list, each value in the list is associated with the differenace from the starting value to the maximum value for the column
# starting value takes in a list, each value in the list is associated with the minimum value for the column
def generate_sobol_sample(num_of_var, num_of_sets, var_range, starting_value):
    n: ndarray = np.array(sobol(num_of_var, num_of_sets))
    if len(var_range) > 1:
        for count, num in enumerate(var_range):
            temp = [num]
            n[:, count] *= temp
    else:
        n = n * var_range

    if len(starting_value) > 1:
        for count, num in enumerate(starting_value):
            temp = [num]
            n[:, count] = n[:, count] + temp
    else:
        n = n + starting_value
    return n


def pass_operator_as_arg(operator, og_val, compare_val):
    if operator == '>=':
        if og_val >= compare_val:
            return True
        else:
            return False

    if operator == '<=':
        if og_val <= compare_val:
            return True
        else:
            return False

    if operator == '>':
        if og_val > compare_val:
            return True
        else:
            return False

# takes in a dict {year:month : value}
# this is a one step more function for split_data_into_month()
# the year month is string instead of date object
# return a dict of dict
def sort_data_to_monthly(the_dict):
    sorted_data = {}
    year_month = list(the_dict.keys())
    for val in year_month:
        try:
            month = val.split(':')[1]
            if month in list(sorted_data.keys()):
                sorted_data[month][val] = the_dict[val]
            else:
                sorted_data[month] = {}
                sorted_data[month][val] = the_dict[val]
        except Exception as e:
            print(e)

    return sorted_data


# return the mean of the values in the passed in object
# return format: {year:mean}
def return_mean_for_each_key(the_dict):
    return_dict = {k: statistics.mean(v) for k, v in the_dict.items()}
    return return_dict


def return_sum_for_each_key(the_dict):
    return_dict = {k: sum(v) for k, v in the_dict.items()}
    return return_dict


def return_min_for_each_key(the_dict):
    return_dict = {k: min(v) for k, v in the_dict.items()}
    return return_dict


def return_max_for_each_key(the_dict):
    return_dict = {k: max(v) for k, v in the_dict.items()}
    return return_dict


# the function finds the duration of the given dict value
# takes in the full value dict,{date:val,...} and a threshold for the duration, the key is date object
# return a list of durations for each year
def find_duration(the_dict, threshold, operator):
    sorted_data = {}
    val_duration = 0
    for val in the_dict:
        if val.year not in sorted_data.keys():
            sorted_data[val.year] = {}
        if pass_operator_as_arg(operator, the_dict[val], threshold):
            val_duration = val_duration + 1
        elif val_duration > 1:
            end_date = val
            if 'all_data' in sorted_data[val.year].keys():
                sorted_data[val.year]['all_data'].append({'date_range':
                                                              (datetime.strftime(start_date, '%Y-%m-%d') +
                                                               '-' +
                                                               datetime.strftime(end_date, '%Y-%m-%d')),
                                                          'duration':
                                                              val_duration})
            else:
                sorted_data[val.year]['all_data'] = []
                sorted_data[val.year]['all_data'].append({'date_range':
                                                              (datetime.strftime(start_date, '%Y-%m-%d') +
                                                               '-' +
                                                               datetime.strftime(end_date, '%Y-%m-%d')),
                                                          'duration':
                                                              val_duration})
            val_duration = 0

        if val_duration == 1:
            start_date = val

    return sorted_data


# takes in the duration dict as the input, calculate the sum of the duration for each given year
def sum_of_duration(the_dict):
    new_dict = {k: v for k, v in the_dict.items() if v}
    new_new_dict = {}
    for k in new_dict:
        sum_list = []
        for value in new_dict[k]['all_data']:
            sum_list.append(value['duration'])
        new_new_dict[k] = sum(sum_list)

    return new_new_dict


# passed in dict is the duration, {year:{'all_data':{'date_range':,duration:''.....}}}
def find_longest_in_duration(duration_dict):
    for val in duration_dict:
        longest = 0
        date_range = ''
        durations_for_the_year = duration_dict[val]['all_data']
        for line in durations_for_the_year:
            if line['duration'] > longest:
                longest = line['duration']
                date_range = line['date_range']
        duration_dict[val] = {date_range: longest}

    return duration_dict


# return the max and min temp from the met file in rzwqm
# return format is {date:temp}
def rzwqm_met_temp(path, whicht):
    # this function parses the met file
    # in met file, 0 is day, 1 is year, 2 is tmin, 3 is tmax
    sorted_list = {}
    with open(path) as f:
        lines = [line.rstrip('\n') for line in f]
    content = lines[36:]
    for line in content:
        split_line = line.split()
        day = split_line[0]
        year = split_line[1]
        tmin = float(split_line[2])
        tmax = float(split_line[3])
        date = datetime.strptime(year + ':' + day, '%Y:%j')
        if whicht == 'avg':
            sorted_list[date] = (tmin + tmax) / 2
        elif whicht == 'min':
            sorted_list[date] = tmin
        elif whicht == 'max':
            sorted_list[date] = tmax

    return sorted_list


def rzwqm_met_rain(path):
    # this function parses the met file
    # in met file, 0 is day, 1 is year, 2 is tmin, 3 is tmax
    sorted_list = {}
    with open(path) as f:
        lines = [line.rstrip('\n') for line in f]
    content = lines[36:]
    for line in content:
        split_line = line.split()
        day = split_line[0]
        year = split_line[1]
        rain = float(split_line[9])
        date = datetime.strptime(year + ':' + day, '%Y:%j')
        sorted_list[date] = rain
    return sorted_list


def rzwqm_met_solar(path):
    # this function parses the met file
    # in met file, 0 is day, 1 is year, 2 is tmin, 3 is tmax
    sorted_list = {}
    with open(path) as f:
        lines = [line.rstrip('\n') for line in f]
    content = lines[36:]
    for line in content:
        split_line = line.split()
        day = split_line[0]
        year = split_line[1]
        rain = float(split_line[9])
        date = datetime.strptime(year + ':' + day, '%Y:%j')
        sorted_list[date] = rain
    return sorted_list


def zero_to_nan(values):
    """Replace every 0 with 'nan' and return a copy."""
    return [float('nan') if x == 0 else x for x in values]


def split_years():
    dates = {}
    ob_list = {}
    sim_list = {}
    try:
        for i in range(2000, 2021):
            print(i)
            the_year = str(i)
            the_dates = []
            ob_temp = []
            sim_temp = []
            for count, val in enumerate(ob):
                date = datetime.strptime(val[0], ('%Y-%m-%d'))
                year = date.year
                if i == year:
                    the_dates.append(date)
                    ob_temp.append(float(val[1]))
                    sim_temp.append(float(sim[count]))
            dates[the_year] = the_dates
            ob_list[the_year] = ob_temp
            sim_list[the_year] = sim_temp
        # print(dates)
    except Exception as e:
        print(e)

    print(dates)
    for val in dates.keys():
        fig, ax = plt.subplots()
        ax.plot(dates[val], ob_list[val], label='ob')
        ax.plot(dates[val], sim_list[val], label='sim')
        ax.set_title(val)
        ax.xaxis.set_major_formatter(years_fmt)
        ax.legend()
        plt.show()


def value_dates_binding(dates, data):
    re = {}
    for count, date in enumerate(dates):
        if math.isnan(data[count]):
            continue
        else:
            re[date] = data[count]

    return re


def write_to_csv_soil(path, data):
    with open(path, 'w') as result_file:
        for line in data:
            result_file.write(str(line))
            result_file.write("\n")


def write_files_from_list_of_lists_to_csv(list_of_dict, name_list, variable_name, date_format='%Y/%m/%d',
                                          keyisdate=True):
    for num, item in enumerate(list_of_dict):
        with open(name_list[num] + " " + variable_name + '.csv', 'w', newline='\n') as result_file:
            writer = csv.writer(result_file)
            for key, value in item.items():
                if keyisdate:
                    writer.writerow([key.strftime(date_format), value])
                else:
                    writer.writerow([key, value])


def write_dict_to_csv(the_dict, path):
    with open(path, 'w', newline='\n') as result_file:
        writer = csv.writer(result_file)
        for key, value in the_dict.items():
            writer.writerow([key.strftime('%Y/%m/%d'), value])


def exclude_data_for_desired_year(year_list, data_dict):
    refined_data = {}
    for date in data_dict:
        if date.year in year_list:
            continue
        else:
            refined_data[date] = data_dict[date]
    return refined_data


def exclude_data_for_desired_year_in_desired_month(year_list, month_list, data_dict):
    refined_data = {}
    for date in data_dict:
        if date.year in year_list:
            if date.month in month_list:
                continue
            else:
                refined_data[date] = data_dict[date]
        else:
            refined_data[date] = data_dict[date]
    return refined_data


def include_data_for_desired_year(year_list, data_dict):
    refined_data = {}
    for date in data_dict:
        if date.year in year_list:
            refined_data[date] = data_dict[date]
        else:
            continue
    return refined_data


def include_data_for_desired_month(month_list, data_dict):
    refined_data = {}
    for date in data_dict:
        if date.month in month_list:
            refined_data[date] = data_dict[date]
        else:
            continue
    return refined_data


def read_frozen_depth(frozen_data_path):
    frozen_data = read_the_file_split_text(frozen_data_path)
    # in the shawdepth.out file, 0 is day of year, 1 is hour, 2 is year, 3 is frozen depth,4 is thaw depth, 5 is snow_depth
    temp_list = []
    sorted_list = {}
    frozen_data = frozen_data[4:]
    for count, line in enumerate(frozen_data):
        dy = line[0]
        year = line[2]
        frozen_depth_val = 0
        last_value_frozen_depth_val = float(frozen_data[count - 1][3])
        if not math.isnan(float(line[3])):
            frozen_depth_val = float(line[3])
        current_date = datetime.strptime(dy + ':' + year, '%j:%Y')
        try:
            dy_next = frozen_data[count + 1][0]
            year_next = frozen_data[count + 1][2]
            next_date = datetime.strptime(dy_next + ':' + year_next, '%j:%Y')
            if current_date == next_date:
                if last_value_frozen_depth_val * 1.2 < frozen_depth_val:
                    temp_list.append(frozen_depth_val)
                else:
                    temp_list.append(last_value_frozen_depth_val)
            else:
                if last_value_frozen_depth_val * 1.2 < frozen_depth_val:
                    temp_list.append(frozen_depth_val)
                else:
                    temp_list.append(last_value_frozen_depth_val)
                x = [i for i in temp_list if i != 0]
                sorted_list[current_date] = statistics.mean(x)
                temp_list = []
        except Exception as e:
            temp_list.append(frozen_depth_val)
            sorted_list[current_date] = statistics.mean(temp_list)
    return sorted_list


def read_thaw_depth(frozen_data_path):
    frozen_data = read_the_file_split_text(frozen_data_path)
    # in the shawdepth.out file, 0 is day of year, 1 is hour, 2 is year, 3 is frozen depth,4 is thaw depth, 5 is snow_depth
    temp_list = []
    sorted_list = {}
    frozen_data = frozen_data[4:]
    for count, line in enumerate(frozen_data):
        dy = line[0]
        year = line[2]
        frozen_depth_val = 0
        last_value_frozen_depth_val = float(frozen_data[count - 1][4])
        if not math.isnan(float(line[4])):
            frozen_depth_val = float(line[4])
        current_date = datetime.strptime(dy + ':' + year, '%j:%Y')
        try:
            dy_next = frozen_data[count + 1][0]
            year_next = frozen_data[count + 1][2]
            next_date = datetime.strptime(dy_next + ':' + year_next, '%j:%Y')
            if current_date == next_date:
                if last_value_frozen_depth_val * 1.2 < frozen_depth_val:
                    temp_list.append(frozen_depth_val)
                else:
                    temp_list.append(last_value_frozen_depth_val)
            else:
                if last_value_frozen_depth_val * 1.2 < frozen_depth_val:
                    temp_list.append(frozen_depth_val)
                else:
                    temp_list.append(last_value_frozen_depth_val)
                x = [i for i in temp_list if i != 0]
                sorted_list[current_date] = statistics.mean(x)
                temp_list = []
        except Exception as e:
            temp_list.append(frozen_depth_val)
            sorted_list[current_date] = statistics.mean(temp_list)
    return sorted_list


def delete_missing(sim, ob):
    delete_keys = []
    for key in sim.keys():
        if not key in ob.keys():
            delete_keys.append(key)
    for k, v in list(sim.items()):
        if k in delete_keys:
            del sim[k]
    return sim


def delete_missing_ob(sim, ob):
    delete_keys = []
    for key in ob.keys():
        if not key in sim.keys():
            delete_keys.append(key)
    for k, v in list(ob.items()):
        if k in delete_keys:
            del ob[k]
    return ob


def finding_max_for_each_dict(temp, snow, frozen_depth_here, temp_which, snow_which, soil_temp):
    winter_temp = split_data_into_years(temp)
    if temp_which == 'avg':
        winter_temp_average = list({k: statistics.mean(v) for k, v in winter_temp.items()}.values())
    elif temp_which == 'min':
        winter_temp_average = list({k: min(v) for k, v in winter_temp.items()}.values())
    elif temp_which == 'max':
        winter_temp_average = list({k: max(v) for k, v in winter_temp.items()}.values())
    yearly_frozen_depth = split_data_into_years(frozen_depth_here)
    frozen_depth_maximum = list({k: max(v) for k, v in yearly_frozen_depth.items()}.values())
    soil_temp_yearly = split_data_into_years(soil_temp)
    soil_temp_here = list({k: statistics.mean(v) for k, v in soil_temp_yearly.items()}.values())
    sim_winter_snow_yearly = split_data_into_years(snow)
    if snow_which == 'avg':
        sim_winter_snow_yearly = list({k: statistics.mean(v) for k, v in sim_winter_snow_yearly.items()}.values())
    elif snow_which == 'max':
        sim_winter_snow_yearly = list({k: max(v) for k, v in sim_winter_snow_yearly.items()}.values())

    return [winter_temp_average, sim_winter_snow_yearly, frozen_depth_maximum, soil_temp_here]


def finding_max_for_each_dict_with_dates(temp, snow, frozen_depth_here):
    yearly_frozen_depth = split_data_into_years_with_dates(frozen_depth_here)
    frozen_depth_maximum = [max(values, key=values.get) for key, values in yearly_frozen_depth.items()]
    sim_winter_snow_yearly = split_data_into_years_with_dates(snow)
    sim_winter_snow_yearly = [max(values, key=values.get) for key, values in sim_winter_snow_yearly.items()]


def finding_max_for_each_dict_monthly(temp, snow, frozen_depth_here):
    winter_temp = include_data_for_desired_month(temp, [1, 2])


def bind_daily(winter_month, temp, snow, frozen, soil_temp):
    snow_val = include_data_for_desired_month(winter_month, snow)
    temp = delete_missing(temp, snow_val)
    frozen = delete_missing(frozen, snow_val)
    soil_temp = delete_missing(soil_temp, snow_val)
    snow_val = list(snow_val.values())
    temp = list(temp.values())
    frozen = list(frozen.values())
    soil_temp = list(soil_temp.values())
    return [temp, snow_val, frozen, soil_temp]


def duration_count_average(data, threshold):
    # the function takes in a dict of data, and a duration threshold
    years_with_duration = {}
    for key, item in data.items():
        n = 0
        for key, daily_item in item.items():
            if daily_item >= threshold:
                n = n + 1
            # elif n > 0:
            #     yearly_duration.append(n)
            #     n = 0
        try:
            years_with_duration[key] = n
        except ValueError:
            years_with_duration[key] = 0
            continue
    return years_with_duration


def thaw_date_rzwqm(data):
    # the idea here for the thaw date is the date where the soil is compeltely thawed.
    # It is determined to be the last thaw event in that year.
    # passed in data should be parsed into yearly data. format: {year:{dates:data,....}}
    thaw_date_for_each_year = {}
    for year in data:
        yearly_data = data[year]
        for count, date in enumerate(yearly_data):
            next_day = date + timedelta(days=1)
            prev_day = date - timedelta(days=1)
            try:
                if yearly_data[date] != 0 and yearly_data[next_day] != 0 and yearly_data[prev_day] == 0:
                    yearly_thaw_date = date
                if count == 181:
                    thaw_date_for_each_year[year] = yearly_thaw_date
                    break
            except Exception as e:
                print(e)
                print(f'for {year}, there is no thaw date ')
                continue
    return thaw_date_for_each_year
