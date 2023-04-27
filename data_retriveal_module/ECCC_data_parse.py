# from db_functions import read_file_path_in_dir_custom
import csv
import json
import os
from datetime import datetime, timedelta

from data_retriveal_module.find_the_index_for_variable import find_the_index
# example format for a file name:en_climate_hourly_QC_702FHL8_12-2020_P1H
from central_database_control_module.db_functions import read_file_path_in_dir_custom
import statistics


def name_to_date(path, dailyorhourly='daily'):
    name = path.split('_')
    # 6th in the list is the date
    print(name)
    if dailyorhourly == 'hourly':
        date = datetime.strptime(name[5], '%d-%Y')
    elif dailyorhourly == 'daily':
        date = datetime.strptime(name[5], '%Y')
    return date


def read_the_file(path):
    with open(path, encoding="utf8", errors='ignore') as f:
        lines = [line.rstrip('\n') for line in f]
    parsed_data_all = []
    for data in lines:
        parsed_data = data.split(',')
        parsed_data_all.append(parsed_data)
    return parsed_data_all


def write_to_csv(path, s):
    with open(path, 'a', encoding='utf8', newline='') as output_file:
        fc = csv.DictWriter(output_file,
                            fieldnames=s[0].keys(),
                            )
        fc.writeheader()
        fc.writerows(s)


def write_to_to_csv_list_of_lists(path, s):
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(s)


def write_to_to_csv_list_of_lists_a(path, s):
    with open(path, "a", newline="", encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(s)


def read_all_and_write_to_one(path, write_to_name, dailyorhourly):
    all_data = []
    paths = read_file_path_in_dir_custom(path, '.csv')
    header = ''
    for count, val in enumerate(paths):
        the_date = name_to_date(val, dailyorhourly)
        data = read_the_file_split(os.path.join(path, val))
        if count == 0:
            # get the header value
            header = data[0]
        del data[0]
        if dailyorhourly == 'hourly':
            data = sort_hourly(data, '%Y-%m-%d %H:%M', header, 'RH')
            data = [[x, statistics.mean(data[x])] for x in data]
        all_data.append({'the_date': the_date, 'data': data})
    # sort the data based on date
    all_data.sort(key=lambda x: x['the_date'])
    # add header, the first line
    all_data[0]['data'].insert(0, header)
    for val in all_data:
        write_to_to_csv_list_of_lists_a(write_to_name, val['data'])




def check_missing_day(path, fmt='%Y-%m-%d', create_csv=False):
    # fmt = '%d/%m/%Y'
    parsed_data_all = read_the_file(path)
    title = parsed_data_all[0]
    var_position = find_the_column(title)
    days = 0
    del parsed_data_all[0]
    # all the lines has been splited into list of lists.
    for count, splitted_data in enumerate(parsed_data_all):
        try:
            date_current = datetime.strptime((parsed_data_all[count])[var_position['date']], fmt)
            date_next = datetime.strptime((parsed_data_all[count + 1])[var_position['date']], fmt)
            days = (date_next - date_current).days
        except Exception as e:
            pass
        if days > 1:
            print(days)
            print(f"Missing date at {date_current}")
            num = count
            for i in range(days - 1):
                date_current = date_current + timedelta(days=1)
                parsed_data_all.insert(num + 1, [str(date_current.strftime('%d/%m/%Y'))])
                num = num + 1
    # push the first line back in
    parsed_data_all.insert(0, title)
    desired_data = desired_columns(parsed_data_all)
    if create_csv:
        write_to_to_csv_list_of_lists('test_check_data.csv', desired_data)
    return parsed_data_all, var_position


def desired_columns(data):
    title = data[0]
    column_dict = find_the_column(title)
    data_with_only_desired_fields = []
    for val in data:
        temp_list = append_to_column(val, column_dict)
        data_with_only_desired_fields.append(temp_list)
    return data_with_only_desired_fields


def append_to_column(data, title):
    temp_list = [data[0]]
    for count, val in enumerate(data):
        if count in title.values():
            temp_list.append(data[count])
    return temp_list


def find_the_column(title):
    eccc_var = {}

    for count, val in enumerate(title):
        find = find_the_index(val)
        if find.find_min_temp():
            eccc_var['min'] = count
        elif find.find_max_temp():
            eccc_var['max'] = count
        elif find.find_rain():
            eccc_var['rain'] = count
        elif find.find_snow():
            eccc_var['snow'] = count
        elif find.find_RH():
            eccc_var['RH'] = count
        elif find.find_date():
            eccc_var['date'] = count
        elif find.find_solar():
            eccc_var['solar'] = count
        elif find.find_wind():
            eccc_var['wind'] = count
        elif find.find_temp():
            eccc_var['temp'] = count
        elif find.find_snowfall():
            eccc_var['snowfall'] = count

    return eccc_var

def read_json(path_name):
    with open(path_name) as f:
        data = json.load(f)
    return data

def nasa_sort_hourly(path):
    # this function is to sort hourly nasa function into a list of lists
    # each list in the big list contains the value for every 24 hour data
    with open(path) as f:
        lines = [line.rstrip('\n') for line in f]
        del lines[0]

    datas = []
    oneday = []
    for count, data in enumerate(lines):
        if count != 0 and (count + 1) % 24 == 0:
            datas.append(oneday)
            oneday = []
        else:
            data = data.split(',')
            oneday.append(data)
    return datas


def check_RH_val(data, i):
    if float(data[i]) > 100:
        return False
    else:
        return True


def fast_scandir(dirname):
    subfolders = [f.path for f in os.scandir(dirname) if f.is_dir()]
    for dirname in list(subfolders):
        subfolders.extend(fast_scandir(dirname))
    return subfolders


def sort_hourly(data, fmt, header, val_col):
    sorted_data = {}
    var_position = find_the_column(header)
    for count, line in enumerate(data):
        date = datetime.strptime(line[var_position['date']], fmt)
        date_pre = datetime.strptime(data[count - 1][var_position['date']], fmt)
        try:
            if date.day == date_pre.day and count != 0:
                if line[var_position[val_col]] != 'NULL' or line[var_position[val_col]]!= '':
                    sorted_data[date.strftime('%Y-%m-%d')].append(float(line[val_col]))
            else:
                sorted_data[date.strftime('%Y-%m-%d')] = []
                sorted_data[date.strftime('%Y-%m-%d')] = []
                if line[var_position[val_col]] != 'NULL' or line[var_position[val_col]] != '':
                    sorted_data[date.strftime('%Y-%m-%d')].append(float(line[val_col]))
        except Exception as e:
            sorted_data[date.strftime('%Y-%m-%d')].append(0)
            continue

    return sorted_data


def handle_data_not_daily_to_daily(data, interval, average=True):
    sorted_list = []
    temp_list = []
    for count, line in enumerate(data):
        val = 0
        if line != 'NaN' or line != '':
            val = float(line)
        if (count + 1) % interval == 0:
            if not average:
                temp_list.append(val)
                no_zero = [n for n in temp_list if n != 0]
                print(no_zero)
                if len(no_zero) > 0:
                    sorted_list.append(no_zero)
                temp_list = []
            else:
                temp_list.append(val)
                no_zero = [n for n in temp_list if n != 0]
                if len(no_zero) > 0:
                    sorted_list.append(round(statistics.mean(no_zero), 2))
                else:
                    sorted_list.append(0)
                temp_list = []
        else:
            temp_list.append(val)
    return sorted_list



