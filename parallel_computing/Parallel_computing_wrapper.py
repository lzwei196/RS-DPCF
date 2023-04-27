import os
import random
import shutil
import statistics
import time
import subprocess

from rzwqm.rzwqm_file import RZWQM, find_desired_line_numbers
from data_handle.direct_env_data_handle import write_to_to_csv_list_of_lists, read_json
# change import directory for db commands for different sql instance

from datetime import datetime, timedelta
import json
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from stats.stat import nse, nse_with_dates, MBE, ioa_with_dates, rmsd_with_dates, pearson_r, quality_check


soil_hydraulic_properties_identifier = {
    'head': '= . . . Repeat for each horizon',
    'end': '=        SOIL HORIZON HEAT MODEL PARAMETERS'
}

albedo_identifier = {
    'head': '=    21      Maxiumum Crop Coefficient                         [0.0-1.3]',
    'end': '==                 S U R F A C E   R E S I D U E                      =='
}

snow_identifier = {
    'head': '=   1.5    PRECIP ALL SNOW IF MAX TEMPERATURE BELOW THIS VALUE [F]',
    'end': '=     ALBEDO ADJUSTMENTS'
}

canada_soil_temp_code_to_depth = {
    1: '134',
    5: '135',
    10: '136',
    20: '137',
    50: '138',
    100: '139',
    150: '140'
}


def rzwqm_parse_layer(desired_depth, file, head_end, column_num):
    # desired_dates = return_layer_date_count('2000-01-01', '2005-12-31', 11, 4, '%Y-%m-%d')
    content = file[head_end:]
    parsed_content = []
    for line in content:
        split_line = line.split()
        parsed_content.append(split_line)
    return_obj = {}
    for data in parsed_content:
        # the_depth is the depth from the layer.plt file
        the_depth = int(float(data[1]))
        # organize the soil temperature based on nodes
        if the_depth in desired_depth:
            try:
                if return_obj[the_depth]:
                    return_obj[the_depth].append(float(data[column_num]))
            except Exception as e:
                return_obj[the_depth] = []
                return_obj[the_depth].append(float(data[column_num]))
    return return_obj


def calibrate_snow(station, depth):
    duration_for_station = \
        select_one_value_from_a_col_with_condition('simulation period', 'soil_info_for_station', 'Station_id', station)[
            0]
    duration_for_station_split = duration_for_station.split('-')
    start_date = datetime.strptime(duration_for_station_split[0] + '0101', '%Y%m%d')
    end_date = datetime.strptime(duration_for_station_split[-1] + '1231', '%Y%m%d')
    nse_env = select_one_col_with_highest_value('NSE_with_NASA', station + 'snow_cali',
                                                'NSE_with_NASA,MB_NASA, the_id,snow_data')
    nse = select_one_col_with_highest_value('NSE', station + 'snow_cali', 'NSE,MBE,the_id, snow_data')
    if nse_env[3] is None:
        soil_sim_record_id = nse[2]
    elif nse[3] is None:
        soil_sim_record_id = nse_env[2]
    elif nse[3] is None and nse_env[3] is None:
        print(station, 'more calibration demanded')
        return
    elif nse_env[0] > nse[0] and nse_env[0] != nse[0]:
        soil_sim_record_id = nse_env[2]
    elif nse[0] > nse_env[0] and nse[0] != nse_env[0]:
        soil_sim_record_id = nse[2]
    else:
        if nse_env[1] == 0:
            soil_sim_record_id = nse[2]
        elif nse[1] == 0:
            soil_sim_record_id = nse_env[2]
        elif nse_env[1] > nse[1]:
            soil_sim_record_id = nse[2]
        else:
            soil_sim_record_id = nse_env[2]
    try:
        ob_soil_raw = select_multiple_col_based_on_date_range(start_date, end_date, station,
                                                              'date,' + 'soil_temp_' + depth)
        ob_soil = query_data_to_datetime_val_format(ob_soil_raw)
        date_range = date_range_list(start_date, end_date)
        sim_soil = select_one_value_from_a_col_with_condition('snow_data', station + 'snow_cali', 'the_id',
                                                              soil_sim_record_id)
        sim_soil = list(json.loads(sim_soil[0]).values())[0]
        sim_soil_with_date = {}
        for count, date in enumerate(date_range):
            sim_soil_with_date[date] = sim_soil[count]
        ob_soil = include_data_for_desired_month([11, 12, 1, 2, 3, 4], ob_soil)
        # ob_soil_average = statistics.mean(
        #     [v for k, v in ob_soil.items() if v is not None and v != 999 and v != -9999.9 and v != 0])
        sim_soil_with_date = include_data_for_desired_month([11, 12, 1, 2, 3, 4], sim_soil_with_date)
        print(station, depth, MBE(sim_soil_with_date, ob_soil))
        return {depth: MBE(sim_soil_with_date, ob_soil)}
    except IndexError as e:
        print(station, depth)
        print(len(ob_soil))
        print(len(sim_soil))
        print(len(date_range))
        return {depth: 'error'}
    except Exception as e:
        # print(station, depth, e)
        return {depth: 'error'}


def calibrate_soil(station, depth):
    duration_for_station = \
        select_one_value_from_a_col_with_condition('simulation period', 'soil_info_for_station', 'Station_id', station)[
            0]
    duration_for_station_split = duration_for_station.split('-')
    start_date = datetime.strptime(duration_for_station_split[0] + '0101', '%Y%m%d')
    end_date = datetime.strptime(duration_for_station_split[-1] + '1231', '%Y%m%d')
    nse_env = select_one_col_with_highest_value('NSE_with_NASA', station + 'snow_cali',
                                                'NSE_with_NASA,MB_NASA, the_id,snow_data')
    nse = select_one_col_with_highest_value('NSE', station + 'snow_cali', 'NSE,MBE,the_id, snow_data')
    if nse_env[3] is None:
        soil_sim_record_id = nse[2]
    elif nse[3] is None:
        soil_sim_record_id = nse_env[2]
    elif nse[3] is None and nse_env[3] is None:
        print(station, 'more calibration demanded')
        return
    elif nse_env[0] > nse[0] and nse_env[0] != nse[0]:
        soil_sim_record_id = nse_env[2]
    elif nse[0] > nse_env[0] and nse[0] != nse_env[0]:
        soil_sim_record_id = nse[2]
    else:
        if nse_env[1] == 0:
            soil_sim_record_id = nse[2]
        elif nse[1] == 0:
            soil_sim_record_id = nse_env[2]
        elif nse_env[1] > nse[1]:
            soil_sim_record_id = nse[2]
        else:
            soil_sim_record_id = nse_env[2]

    try:
        # soil_sim_record_id = \
        #     select_one_col_with_highest_value('the_id', station + 'snow_cali', 'the_id')[0]
        ob_soil_raw = select_multiple_col_based_on_date_range(start_date, end_date, station,
                                                              'date,' + 'soil_temp_' + depth)
        ob_soil = query_data_to_datetime_val_format(ob_soil_raw)
        date_range = date_range_list(start_date, end_date)
        sim_soil = select_one_value_from_a_col_with_condition('soil_data' + depth, station + 'snow_cali', 'the_id',
                                                              soil_sim_record_id)
        sim_soil = list(json.loads(sim_soil[0]).values())[0]
        sim_soil_with_date = {}
        for count, date in enumerate(date_range):
            sim_soil_with_date[date] = sim_soil[count]
        ob_soil = include_data_for_desired_month([11, 12, 1, 2, 3, 4], ob_soil)
        ob_soil_average = statistics.mean(
            [v for k, v in ob_soil.items() if v is not None and v != 999 and v != -9999.9 and v != 0])
        sim_soil_average = statistics.mean(
            [v for k, v in sim_soil_with_date.items() if v is not None and v != 999 and v != -9999.9 and v != 0])
        sim_soil_with_date = include_data_for_desired_month([11, 12, 1, 2, 3, 4], sim_soil_with_date)
        print(station, depth, pearson_r(ob_soil, sim_soil_with_date, sim_soil_average, ob_soil_average))
        return {depth: pearson_r(ob_soil, sim_soil_with_date, sim_soil_average, ob_soil_average)}
    except IndexError as e:
        print(station, depth)
        print(len(ob_soil))
        print(len(sim_soil))
        print(len(date_range))
        return {depth: 'error'}
    except Exception as e:
        return {depth: 'error'}


def cali_value_to_key_string(cali_value_list):
    key_str = ''
    for count, val in enumerate(list(cali_value_list.values())):
        if count == len(cali_value_list) - 1:
            key_str = key_str + str(val)
        else:
            key_str = key_str + str(val) + ', '
    return key_str


def include_data_for_desired_month(month_list, data_dict):
    refined_data = {}
    for date in data_dict:
        if date.month in month_list:
            refined_data[date] = data_dict[date]
        else:
            continue



def calibrate_for_one_station(station, project_path, table_name,
                              calibrating_variable_list, calibrating_type, worker_number, instance_number=0):
    # select calibrating value from the database, the status of the value should be "unstarted", 0
    cali_value = select_one_random_value_from_a_col_with_condition('snow_rho_iniandsnow_rho_max',
                                                                   table_name, 'working_status', 0)
    cali_value = cali_value[0][0].split(',')
    cali_value_dict = dict(zip(calibrating_variable_list, cali_value))
    cali_val_in_db = ''
    try:
        # turn cali value into cdb format
        for count, x in enumerate(cali_value):
            if count != len(cali_value) - 1:
                cali_val_in_db = cali_val_in_db + x + ','
            else:
                cali_val_in_db = cali_val_in_db + x
    except Exception as e:
        print(e)

    #update the start time to db
    code_start_time = time.time()
    start_timestamp = datetime.fromtimestamp(code_start_time).strftime('%Y-%m-%d %H:%M:%S')
    update_value_for_a_col_with_for_a_row(table_name, 'iter_start_timestemp',
                                          start_timestamp,
                                          'snow_rho_iniandsnow_rho_max', str(cali_val_in_db))
    total_worker = 8

    # below for thread
    instance_number = 0
    original_station = station
    global instance_working_dict
    for x in instance_working_dict.keys():
        if instance_working_dict[x] == 0:
            instance_number = x
            instance_working_dict[x] = 1
            break
    new_station = station + str(instance_number)
    scenario_path = project_path + station

    # below for process
    # try:
    #     instance_number = instance_number % total_worker
    #     time.sleep(1)
    #     if instance_number == 0:
    #         instance_number = (instance_number + 1) * total_worker
    #     original_station = station
    #     new_station = station + str(instance_number)
    #     scenario_path = project_path + station
    #     f = project_path + new_station + '//RZWQMrelease.exe'
    #     try:
    #         os.rename(f, f)
    #     except OSError as e:
    #         for num in range(1, total_worker):
    #             if os.path.exists(f):
    #                 try:
    #                     new_station = station + str(num)
    #                     new_station_path = project_path+ new_station+'//RZWQMrelease.exe'
    #                     os.rename(new_station_path, new_station_path)
    #                     instance_number = num
    #                     break
    #                 except OSError as e:
    #                     continue


    try:
        # update the status of the parameter to 1, working
        update_value_for_two_cols_for_a_row(table_name, 'working_status', 1, 'worker_number', worker_number,
                                            'snow_rho_iniandsnow_rho_max',
                                            str(cali_val_in_db))

        # write new properties based on the given cali value, cali value should include the var type and the value
        if calibrating_type == 'env_properties':
            write_new_env_prop_values(station, scenario_path, cali_value_dict)
        elif calibrating_type == 'hydraulic_properties':
            write_new_hydraulic_properties(station, scenario_path, cali_value_dict)
        elif calibrating_type == 'snow_properties':
            write_new_snow_prop_values(station, project_path, cali_value_dict, original_station)
    except Exception as e:
        print(e)
        print(station)

    try:
        # start simulation and return simulation time
        rz_simulation_time = start_simulation_for_rzwqm(new_station, project_path, table_name, cali_val_in_db)

        # release the instance
        # instance_working_dict[instance_number] = 0

        update_value_for_a_col_with_for_a_row(table_name, 'rz_simulation_time', rz_simulation_time,
                                              'snow_rho_iniandsnow_rho_max', str(cali_val_in_db))
        total_simulationtime_for_the_iteration = time.time() - code_start_time
        update_value_for_a_col_with_for_a_row(table_name, 'total_simulationtime_for_the_iteration',
                                              total_simulationtime_for_the_iteration,
                                              'snow_rho_iniandsnow_rho_max', str(cali_val_in_db))
        ts = time.time()
        timestamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        update_value_for_a_col_with_for_a_row(table_name, 'iter_finish_timestamp',
                                              timestamp,
                                              'snow_rho_iniandsnow_rho_max', str(cali_val_in_db))
        print(timestamp)
    except Exception as e:
        print(e)
        with open("error.txt", "a") as myfile:
            ts = time.time()
            timestamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            myfile.write(f'\n{timestamp}')
            myfile.write(f'\n{instance_number}')
            myfile.write(f'\n{e}')


def calibrate_soil_one_station(station, scenario_path, table_name,
                               cali_value, observed_value,
                               start_date_input, end_date_input, SHAW):
    # check if the trying values have been simulated, query if the cali value exist in the database
    # res = check_if_a_value_exists_in_a_column(table_name, column_name, str(cali_value.tolist()))

    # if not in the database, write the cali value to rzwqm data and start simulation
    # if res is None:
    write_new_hydraulic_properties(station, scenario_path, cali_value)

    # add soil calibrating parameters first
    add_primary_key_before_simulation(table_name, 'soil_lateral_hydraulics', str(cali_value))
    # run the rz simulation and return the simulation time
    simulation_time = start_simulation_for_rzwqm(station, scenario_path)

    # placeholder for RZWQM class
    rz = RZWQM(scenario_path, '', scenario_path + '/Analysis/' + station + '.ana')

    # retrive tile_drainage from the simulated result
    sim_tile = rz.rzwqm_res_parse('tile_drainage')
    month_list = [11, 12, 1, 2, 3, 4]
    # trim the ob and sim to only the desired range, format yyyy/mm/dd
    start_date = datetime.strptime(start_date_input, '%Y/%m/%d')
    end_date = datetime.strptime(end_date_input, '%Y/%m/%d')

    # trim the sim tile drainage to mm, and cut into winter
    sim_tile_trimmed = {x: float(v) * 10 for x, v in sim_tile.items() if end_date >= x >= start_date}
    sim_tile_trimmed_with_strkey = {x.strftime('%Y/%m/%d'): v for x, v in sim_tile_trimmed.items()}
    winter_sim_tile = include_data_for_desired_month(month_list, sim_tile_trimmed)

    # turn the key for the observed value into datetime format
    observed_value = {datetime.strptime(x[0], '%m/%d/%Y'): x[1] for x in observed_value}
    ob_tile_trimmed = {x: float(v) for x, v in observed_value.items() if end_date >= x >= start_date}
    ob_winter_tile = include_data_for_desired_month(month_list, ob_tile_trimmed)

    # statistical result
    try:
        ob_avg = [v for k, v in ob_tile_trimmed.items() if v is not None]
        ob_avg = statistics.mean(ob_avg)
        ob_avg_winter = [v for k, v in ob_winter_tile.items() if v is not None]
        ob_avg_winter = statistics.mean(ob_avg_winter)
        annual_NSE = nse_with_dates(sim_tile_trimmed, ob_tile_trimmed, ob_avg)
        annual_mbe = MBE(sim_tile_trimmed, ob_tile_trimmed)
        winter_NSE = nse_with_dates(winter_sim_tile, ob_winter_tile, ob_avg_winter)
        winter_mbe = MBE(winter_sim_tile, ob_winter_tile)
        add_tile_drainage_performance_calibration_record(table_name,
                                                         'soil_lateral_hydraulics', str(cali_value),
                                                         'all_year_tile_NSE', annual_NSE,
                                                         'Winter_tile_NSE', winter_NSE,
                                                         'all_year_tile_MBE', annual_mbe,
                                                         'Winter_tile_MBE', winter_mbe,
                                                         'simulation_time', simulation_time,
                                                         'sim_tile_drainage_data',
                                                         json.dumps(sim_tile_trimmed_with_strkey),
                                                         'SHAW', SHAW
                                                         )
    except Exception as e:
        print(e)
        add_tile_drainage_performance_calibration_record(table_name,
                                                         'soil_lateral_hydraulics', str(cali_value),
                                                         'all_year_tile_NSE', annual_NSE,
                                                         'Winter_tile_NSE', winter_NSE,
                                                         'all_year_tile_MBE', annual_mbe,
                                                         'Winter_tile_MBE', winter_mbe,
                                                         'simulation_time', simulation_time,
                                                         'sim_tile_drainage_data',
                                                         json.dumps(sim_tile_trimmed_with_strkey),
                                                         'SHAW', SHAW)
        print(f'task {cali_value} simulated')


def start_simulation_for_rzwqm(station, scenario_path, table_name, cali_val_in_db):
    rz_path = scenario_path + station + '//RZWQMrelease.exe'
    cmd_path = scenario_path + station
    try:
        start = time.time()
        rz_start_timestamp = datetime.fromtimestamp(start).strftime('%Y-%m-%d %H:%M:%S')
        update_value_for_a_col_with_for_a_row(table_name, 'rz_start_timestemp',
                                              rz_start_timestamp,
                                              'snow_rho_iniandsnow_rho_max', str(cali_val_in_db))
        subprocess.run(rz_path, cwd=r'{}'.format(cmd_path))
        time.sleep(2)
        end = time.time()
        rz_finish_timestamp = datetime.fromtimestamp(end).strftime('%Y-%m-%d %H:%M:%S')
        update_value_for_a_col_with_for_a_row(table_name, 'rz_finish_timestemp',
                                              rz_finish_timestamp,
                                              'snow_rho_iniandsnow_rho_max', str(cali_val_in_db))
    except Exception as e:
        print(e)
    return end - start


def write_new_hydraulic_properties(scenario_name, scenario_path, new_value):
    station = scenario_name
    path = scenario_path
    rzwqm = RZWQM(path, station)
    head, end = find_desired_line_numbers(soil_hydraulic_properties_identifier['head'],
                                          soil_hydraulic_properties_identifier['end'], rzwqm.dat_data, 2, 2)
    soil_hydraulic_properties = rzwqm.return_the_soil_properties_class(head, end)
    for num in range(len(new_value)):
        setattr(soil_hydraulic_properties[num + 1], 'lateral_ksat', new_value[num])
    rzwqm.write_new_hydraulic_properties_to_dat(soil_hydraulic_properties, head, end)


def write_new_env_prop_values(scenario_name, scenario_path, new_value):
    station = scenario_name
    path = scenario_path
    rzwqm = RZWQM(path, station)
    head, end = find_desired_line_numbers(albedo_identifier['head'],
                                          albedo_identifier['end'], rzwqm.dat_data, 3, 3)
    environment_properties = rzwqm.env_prop(end, rzwqm.dat_data)
    for prop in list(new_value.keys()):
        environment_properties[prop] = new_value[prop]
    rzwqm.write_env_pop_to_dat(environment_properties, rzwqm.dat_data, end)


def write_new_snow_prop_values(scenario_name, project_path, new_value, original_station_name):
    station = scenario_name
    path = project_path
    rzwqm = RZWQM(path, station)
    if len(rzwqm.sno_data) == 0:
        shutil.copyfile(project_path + 'Meteorology//' + original_station_name + '.sno',
                        project_path + 'Meteorology//' + station + '.sno')
    head, end = find_desired_line_numbers(snow_identifier['head'],
                                          snow_identifier['end'], rzwqm.sno_data, 2, 2)
    snow_lines = rzwqm.sno_data
    sno_line = snow_lines[end].split()
    sno_line[0] = new_value['snow_max']
    sno_line[1] = new_value['snow_ini']
    sno_line_d = ''
    for count, val in enumerate(sno_line):
        if count != (len(sno_line) - 1):
            sno_line_d = sno_line_d + str(val) + '  '
        else:
            sno_line_d = sno_line_d + str(val)
    snow_lines[end] = sno_line_d
    with open(rzwqm.sno_path, 'w') as file:
        for line in snow_lines:
            file.write(line + '\n')


def reformat_nse_dict(the_data):
    reformat = []
    keys = [list(x.keys())[0] for x in the_data[list(the_data.keys())[0]]]
    keys.insert(0, 'station')
    reformat.append(keys)
    for station in the_data:
        value_list = [list(x.values())[0] for x in the_data[station]]
        value_list.insert(0, station)
        reformat.append(value_list)
    return reformat


def return_soil_nse_for_all_station(crop_stations, file_name):
    final_nse = {}
    for station in crop_stations:
        final_nse[station] = []
        for depth in ['134', '135', '136', '137', '138', '139']:
            obj = calibrate_soil(station, depth)
            final_nse[station].append(obj)
    reformat = reformat_nse_dict(final_nse)
    write_to_to_csv_list_of_lists(file_name, reformat)


def date_range_list(start_date, end_date):
    # Return list of datetime.date objects between start_date and end_date (inclusive).
    date_list = []
    curr_date = start_date
    while curr_date <= end_date:
        date_list.append(curr_date)
        curr_date += timedelta(days=1)
    return date_list


def combine_date_and_val(date_range, val):
    obj = {}
    for count, date in enumerate(date_range):
        obj[date] = val[count]
    return obj


def combine_str_date_and_val(date_range, val):
    obj = {}
    for count, date in enumerate(date_range):
        obj[date.strftime("%Y/%m/%d")] = val[count]
    return obj


def include_data_for_desired_month(month_list, data_dict):
    refined_data = {}
    for date in data_dict:
        if date.month in month_list:
            refined_data[date] = data_dict[date]
        else:
            continue
    return refined_data


def copytree(src, dst, symlinks=False, ignore=None):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
                shutil.copy2(s, d)


def met_value(station):
    duration_for_station = \
        select_one_value_from_a_col_with_condition('simulation period', 'soil_info_for_station', 'Station_id', station)[
            0]
    duration_for_station_split = duration_for_station.split('-')
    start_date = datetime.strptime(duration_for_station_split[0] + '0101', '%Y%m%d')
    end_date = datetime.strptime(duration_for_station_split[-1] + '1231', '%Y%m%d')
    met_value = select_multiple_col_based_on_date_range(start_date, end_date, station, 'minimum_air_temp,max_air_temp,'
                                                                                       'minimum_air_temp_nasa,'
                                                                                       'max_air_temp_nasa,'
                                                                                       'snow_depth_adjusted,'
                                                                                       'snow_depth_nasa')
    date_range = date_range_list(start_date, end_date)
    min_air = combine_date_and_val(date_range, [x[0] for x in met_value])
    max_air = combine_date_and_val(date_range, [x[1] for x in met_value])
    min_air_nasa = combine_date_and_val(date_range, [x[2] for x in met_value])
    max_air_nasa = combine_date_and_val(date_range, [x[3] for x in met_value])
    min_temp_list = {}
    max_temp_list = {}
    avg_temp_list = {}
    snow_list = {}

    for value in list(min_air.keys()):
        if min_air[value] is not None and min_air[value] != 999 and min_air[value] != 9999:
            min_temp_list[value] = min_air[value]
        else:
            min_temp_list[value] = min_air_nasa[value]

    for value in list(max_air.keys()):
        if max_air[value] is not None and max_air[value] != 999 and max_air[value] != 9999:
            max_temp_list[value] = max_air[value]
        else:
            max_temp_list[value] = max_air_nasa[value]

    for key in list(min_temp_list.keys()):
        min_temp = min_temp_list[key]
        max_temp = max_temp_list[key]
        avg_temp_list[key] = (float(min_temp) + float(max_temp)) / 2

    snow = combine_date_and_val(date_range, [x[4] for x in met_value])
    snow_nasa = combine_date_and_val(date_range, [x[5] for x in met_value])

    for value in list(snow.keys()):
        if snow[value] is not None and snow[value] != 999 and snow[value] != 9999:
            snow_list[value] = snow[value]
        else:
            snow_list[value] = snow_nasa[value]

    return {
        'min_air': min_temp_list,
        'max_air': max_temp_list,
        'snow': snow_list,
        'avg_air': avg_temp_list
    }


def return_nse_for_all_stations():
    crop_stations = read_json('../ca_freeze_thaw/stations_dly12_duration_allpotential.json')
    return_soil_nse_for_all_station(crop_stations, 'pearson-all-year.csv')



def load_config():
    with open('config.json', 'r') as f:
        config = json.load(f)
    return config


# change the soil_hydraulic_properties based on calibration values
if __name__ == '__main__':
    starting_time = time.time()
    worker_number = 1
    project_path = ''
    total_iteration_times = ''
    station = ''
    number_of_instance = ''
    number_list = list(range(1, number_of_instance + 1))
    instance_working_dict = {x: 0 for x in number_list}
    number_of_threads = ''
    config = load_config()

    if config["parallel_mode"] == "MP":
        # process
        executor = ProcessPoolExecutor(max_workers=20)
        for num in range(1, total_iteration_times + 1):
            executor.submit(calibrate_for_one_station, station, project_path, 'lods_mp', ['snow_ini', 'snow_max'],
                            'snow_properties', worker_number, num)
    else:
    # thread
        pool = ThreadPoolExecutor(number_of_threads)
        for num in range(0, total_iteration_times):
            pool.submit(calibrate_for_one_station, station, project_path, 'lods', ['snow_ini', 'snow_max'], 'snow_properties', worker_number, num)
