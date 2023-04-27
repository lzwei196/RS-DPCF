from db_connection import cursor, db
import json
import os


###############################add delete actions
######add delete action
def add_station_env_data(table_name, date, minimum_air_temp, max_air_temp, wind_speed, solar_radiation, RH, snow_depth_adjusted):
    sql = "INSERT INTO `{}`(date, minimum_air_temp, max_air_temp, wind_speed, solar_radiation, RH, snow_depth_adjusted) VALUES (%s, %s, %s, %s, %s, %s, %s) " \
          "ON DUPLICATE KEY UPDATE minimum_air_temp=values(minimum_air_temp), " \
          "max_air_temp=values(max_air_temp), " \
          "wind_speed = values(wind_speed), " \
          "solar_radiation = values(solar_radiation)," \
          "RH = values(RH)," \
          "snow_depth_adjusted = values(snow_depth_adjusted)".format(table_name)
    cursor.execute(sql, (date, minimum_air_temp, max_air_temp,wind_speed,solar_radiation, RH,snow_depth_adjusted))
    db.commit()

def add_station_nasa_data(table_name, date, minimum_air_temp_nasa, max_air_temp_nasa, wind_speed_nasa, solar_radiation_nasa, RH_nasa, total_rain_nasa, snow_depth_nasa):
    sql = "INSERT INTO `{}`(date, minimum_air_temp_nasa, max_air_temp_nasa, wind_speed_nasa, solar_radiation_nasa, RH_nasa, total_rain_nasa, snow_depth_nasa) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)" \
          "ON DUPLICATE KEY UPDATE  minimum_air_temp_nasa=values(minimum_air_temp_nasa), " \
          "max_air_temp_nasa=values(max_air_temp_nasa), " \
          "wind_speed_nasa = values(wind_speed_nasa), " \
          "solar_radiation_nasa = values(solar_radiation_nasa)," \
          "RH_nasa = values(RH_nasa)," \
          "total_rain_nasa = values(total_rain_nasa)," \
          "snow_depth_nasa = values(snow_depth_nasa)".format(table_name)
    cursor.execute(sql, (date, minimum_air_temp_nasa, max_air_temp_nasa,wind_speed_nasa,solar_radiation_nasa, RH_nasa, total_rain_nasa, snow_depth_nasa))
    db.commit()

def add_soil_data(table_name, date, column_name, soil_temp):
    sql = "INSERT INTO `{}`(date, {}) VALUES (%s, %s)" \
          "ON DUPLICATE KEY UPDATE  {}=values({})".format(table_name, column_name, column_name, column_name)
    cursor.execute(sql, (date, soil_temp))
    db.commit()

def add_snow_calibration_nse(table_name, sno_vals,sno_vals_col, nse_value, nse_col):
    sql = "INSERT INTO `{}`({}, {}) VALUES (%s, %s)" \
          "ON DUPLICATE KEY UPDATE  {}=values({}), {}=values({})".\
        format(table_name, sno_vals_col, nse_col, sno_vals_col, sno_vals_col, nse_col, nse_col)
    cursor.execute(sql, (sno_vals, nse_value))
    db.commit()

def add_cweeds_data(table_name, date, cweeds_diffuse_horizontal):
    sql = "INSERT INTO `{}`(date, cweeds_diffuse_horizontal) VALUES (%s, %s)" \
          "ON DUPLICATE KEY UPDATE  cweeds_diffuse_horizontal=values(cweeds_diffuse_horizontal)".format(table_name)
    cursor.execute(sql, (date, cweeds_diffuse_horizontal))
    db.commit()

def add_adjusted_total_rain(table_name, date, total_rain_adjusted):
    sql = "INSERT INTO `{}`(date, total_rain_adjusted) VALUES (%s, %s)" \
          "ON DUPLICATE KEY UPDATE  total_rain_adjusted=values(total_rain_adjusted)".format(table_name)
    cursor.execute(sql, (date, total_rain_adjusted))
    db.commit()


#####select action
def select_dl_eccc_data(year, station_id):
    try:
        sql = "SELECT `file_location` FROM `downloaded_eccc_data` WHERE station_id = ('{}') AND year = ('{}')".format(station_id, year)
        #print(sql)
        cursor.execute(sql)
        result = cursor.fetchone()
        return result
    except Exception as e:
        print(e)

def select_all_from_a_col(col, station):
    try:
        sql = "SELECT `{}` FROM `{}`".format(col, station)
        #print(sql)
        cursor.execute(sql)
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(e)

def select_one_value_from_a_col_with_condition(col_to_choose, table_name, col_condition, condition_value):
    try:
        sql = "SELECT `{}` FROM `{}` WHERE `{}` = '{}'".format(col_to_choose, table_name, col_condition, condition_value)
        cursor.execute(sql)
        result = cursor.fetchone()
        return result
    except Exception as e:
        print(e)

def select_one_col_with_highest_value(col_name, table_name, column_to_be_selected):
    try:
        sql = "SELECT {} FROM {} WHERE {} = (SELECT MAX({}) FROM {})".format(column_to_be_selected,
                                                                             table_name, col_name, col_name, table_name)
        # print(sql)
        cursor.execute(sql)
        result = cursor.fetchone()
        return result
    except Exception as e:
        print(e)


def select_multiple_col_based_on_date_range(start, end,table_name, col_to_choose):
    try:
        sql = "SELECT {} FROM `{}` WHERE `date` BETWEEN '{}' and '{}'".format(col_to_choose, table_name, start, end)
        cursor.execute(sql)
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(e)

def check_if_a_value_exists_in_a_column(table_name, column_name, value):
    try:
        sql = "SELECT * FROM `{}` WHERE {} = '{}'".format(table_name, column_name, value)
        cursor.execute(sql)
        result = cursor.fetchone()
        return  result

    except Exception as e:
        print(e)



####create table
def create_table(Table,table_name, DB_name, the_cursor):
    the_cursor.execute("USE {}".format(DB_name))
    table_description = Table
    try:
            # print(table_description)
            print("creating table ({})".format(table_name), end="")
            the_cursor.execute(table_description)
    except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("Table alreayd exists")
            else:
                print(err.msg)

####change datatype
def change_data_type_for_a_column(station, column, change_to):
        sql = "ALTER TABLE `ca_freeze_thaw`.`{}`MODIFY COLUMN `{}` {};".format(station, column, change_to)
        cursor.execute(sql)
        db.commit()

def change_primary_key_for_a_column(station, column):
    sql = "ALTER TABLE {} MODIFY `id` INT,  DROP PRIMARY KEY, ADD PRIMARY KEY({})".format(station, column)
    cursor.execute(sql)
    db.commit()

def drop_a_column(station, column):
    sql = "ALTER TABLE {} DROP COLUMN {};".format(station, column)
    cursor.execute(sql)
    db.commit()

def rename_a_column(station,column, new_column_name):
    sql = 'ALTER TABLE {} RENAME COLUMN {} TO {}'.format(station, column, new_column_name)
    print(sql)
    cursor.execute(sql)
    db.commit()

####add column to the existing table
def add_column_to_existing_table(table_name, column_name, data_type):
    sql = "ALTER TABLE ca_freeze_thaw.{} ADD {} {}".format(table_name, column_name, data_type)
    cursor.execute(sql)
    db.commit()



def add_env_element(element_code, variable_name):
    sql = "INSERT INTO `env variables`(element_code, variable_name) VALUES (%s, %s)"
    cursor.execute(sql, (element_code, variable_name))
    db.commit()
    id = cursor.lastrowid
    # print("Added elements{}".format(id))


def add_env_element_all():
    data = read_jsonfile("env_elements.json")
    for key, val in data.items():
        add_env_element(key, val)


def add_element_years(element_id, year):
    sql = "INSERT INTO `years_for_each_element`(element_id, year) VALUES (%s, %s)"
    cursor.execute(sql, (element_id, year))
    db.commit()
    id = cursor.lastrowid
    # print("Added elements{}".format(id))


def add_env_dly_date_data(year_id, station_id, month, elementnum):
    sql = "INSERT INTO `env_dly_date_data`(year_id,station_id,month, elementnum) VALUES (%s, %s, %s, %s)"
    # sql = f"INSERT INTO {} (year_id, station_id,month,elementnum) VALUES ({},{},{},{})".format(name,)
    cursor.execute(sql, year_id, station_id, month, elementnum)
    # cursor.execute(sql)
    db.commit()
    id = cursor.lastrowid
    # print("Added elements{}".format(id))
    return id


def add_dly_value(date_data_id, dayinthemonth, value):
    sql = "INSERT INTO `dly_value`(date_data_id,dayinthemonth,value) VALUES (%s, %s, %s)"
    cursor.execute(sql, (date_data_id, dayinthemonth, value))
    db.commit()
    id = cursor.lastrowid
    # print("Added elements{}".format(id))


def sql_execute(thefunc):
    def wrapper(**kwargs):
        sql = thefunc(**kwargs)
        cursor.execute(sql, (kwargs['year_id'], kwargs['station_id'], kwargs['month'], kwargs['elementnum']))
        db.commit()
        id = cursor.lastrowid
        # print("Added elements{}".format(id))
        return id

    return wrapper


def sql_execute_with_val(thefunc):
    def wrapper(**kwargs):
        sql = thefunc(**kwargs)
        cursor.execute(sql, (kwargs['date_data_id'], kwargs['dayinthemonth'], kwargs['value']))
        db.commit()
        id = cursor.lastrowid
        # print("Added elements{}".format(id))
        return id

    return wrapper


@sql_execute
def add_dly_date_data_builder(**kwargs):
    sql = f"INSERT INTO {kwargs['name']} (year_id, station_id, month, elementnum) " \
          f"VALUES (%s, %s, %s, %s)"
    # print(sql)
    return sql


@sql_execute_with_val
def add_dly_value_builder(**kwargs):
    sql = f"INSERT INTO {kwargs['name']} (date_data_id,dayinthemonth,value) VALUES (%s, %s, %s)"
    # print(sql)
    return sql


def add_station_id_val(**kwargs):
    sql = f"INSERT INTO `station_id` (name, province, climate_id, station_id, latitude, longitude, elevation)  VALUES (%s, %s, %s, %s, %s, %s, %s)"
    # print(sql)
    cursor.execute(sql, (
        kwargs['name'], kwargs['province'], kwargs['climate_id'], kwargs['station_id'], kwargs['latitude'],
        kwargs['longitude'], kwargs['elevation']))
    db.commit()
    id = cursor.lastrowid
    print("Added elements{}".format(id))
    return id


def add_station_years(**kwargs):
    sql = "INSERT INTO `station_data_years` (station_id, first_year, last_year, hly_first_year, hly_last_year, " \
          "dly_first_year, dly_last_year, mly_first_year, mly_last_year) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) "
    cursor.execute(sql, (
        kwargs['station_id'], kwargs['first_year'], kwargs['last_year'], kwargs['hly_first_year'],
        kwargs['hly_last_year'],
        kwargs['dly_first_year'], kwargs['dly_last_year'], kwargs['mly_first_year'], kwargs['mly_last_year']))
    db.commit()
    id = cursor.lastrowid
    print("Added elements{}".format(id))
    return id


############################################### select actions
def sql_execute_select(thefunc):
    def wrapper(*args):
        sql = thefunc(args)
        cursor.execute(sql)
        result = cursor.fetchall()
        return result

    return wrapper()


def select_the_elementid(element):
    try:
        sql = ("SELECT element_id FROM `env variables` WHERE element_code = ('{}')".format(element))
        # print(sql)
        cursor.execute(sql)
        result = cursor.fetchone()
        return result
    except Exception as e:
        print(e)


def select_the_station_year_dly(station_id):
    try:
        sql = ("SELECT dly_first_year, dly_last_year FROM station_data_years WHERE  station_id = ('{}')".format(
            station_id))
        # print(sql)
        cursor.execute(sql)
        result = cursor.fetchone()
        return result
    except Exception as e:
        print(e)


def select_the_yearid(year, element):
    sql = ("SELECT year_id FROM years_for_each_element WHERE year = ('{}')  AND element_id = ('{}') ".format(year,
                                                                                                             element))
    cursor.execute(sql)
    result = cursor.fetchone()
    return result


# @sql_execute_select
def select_general_station_id(*args):
    field = args[0]
    val = args[1]
    sql = f"SELECT * FROM station_id WHERE {field} = '{val}'"
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


# document actions

def read_jsonfile(path):
    with open("{}".format(path)) as f:
        elements = json.load(f)
    return elements


# returns the list of the values for each line
def split_functions(s):
    final_obj = {}
    splitted = s.split()
    prefix = splitted[0]
    final_obj['station_id'] = prefix[0:7]
    final_obj['year'] = prefix[7:11]
    final_obj['month'] = prefix[11:13]
    final_obj['elementnum'] = prefix[13:16]
    value_obj = [{'day': '1', 'value': prefix[16:23]}]
    del splitted[0]
    value_obj.extend(split_for_value(splitted))
    final_obj['values'] = value_obj
    return final_obj


###return the values with days in an array
def split_for_value(line):
    value_obj = []
    for i, val in enumerate(line):
        value_obj.append({'day': i + 2, "value": val})
    return value_obj


def read_years_in_dir(path, elementid):
    path_to_data_folder = path
    years = []
    for file in os.listdir(path_to_data_folder):
        if file.endswith(".txt"):
            year = file[11:15]
            add_element_years(elementid, year)
            years.append(year)
    return years


def read_file_path__in_dir(path):
    path_to_data_folder = path
    all_path = []

    for file in os.listdir(path_to_data_folder):
        if file.endswith(".txt"):
            the_path = os.path.join(path, file)
            all_path.append(the_path)

    return all_path

def read_sub_directory_in_dir(path):
    subfolders = [f.path for f in os.scandir(path) if f.is_dir()]
    return subfolders

def read_file_path_in_dir_custom(path, extension):
    path_to_data_folder = path
    all_path = []
    for file in os.listdir(path_to_data_folder):
        if file.endswith(extension):
            # the_path = os.path.join(path, file)
            all_path.append(file)
    return all_path


def value_string_to_num(s):
    if s == '000000' or s == '-99999M':
        return 999
    else:
        res = int(s.strip('0')) / 10
        return res


######add delete action
def add_station_env_data(table_name, date, minimum_air_temp, max_air_temp, wind_speed, solar_radiation, RH, snow_depth_adjusted):
    sql = "INSERT INTO `{}`(date, minimum_air_temp, max_air_temp, wind_speed, solar_radiation, RH, snow_depth_adjusted) VALUES (%s, %s, %s, %s, %s, %s, %s) " \
          "ON DUPLICATE KEY UPDATE minimum_air_temp=values(minimum_air_temp), " \
          "max_air_temp=values(max_air_temp), " \
          "wind_speed = values(wind_speed), " \
          "solar_radiation = values(solar_radiation)," \
          "RH = values(RH)," \
          "snow_depth_adjusted = values(snow_depth_adjusted)".format(table_name)
    cursor.execute(sql, (date, minimum_air_temp, max_air_temp,wind_speed,solar_radiation, RH,snow_depth_adjusted))
    db.commit()

def add_station_nasa_data(table_name, date, minimum_air_temp_nasa, max_air_temp_nasa, wind_speed_nasa, solar_radiation_nasa, RH_nasa, total_rain_nasa, snow_depth_nasa):
    sql = "INSERT INTO `{}`(date, minimum_air_temp_nasa, max_air_temp_nasa, wind_speed_nasa, solar_radiation_nasa, RH_nasa, total_rain_nasa, snow_depth_nasa) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)" \
          "ON DUPLICATE KEY UPDATE  minimum_air_temp_nasa=values(minimum_air_temp_nasa), " \
          "max_air_temp_nasa=values(max_air_temp_nasa), " \
          "wind_speed_nasa = values(wind_speed_nasa), " \
          "solar_radiation_nasa = values(solar_radiation_nasa)," \
          "RH_nasa = values(RH_nasa)," \
          "total_rain_nasa = values(total_rain_nasa)," \
          "snow_depth_nasa = values(snow_depth_nasa)".format(table_name)
    cursor.execute(sql, (date, minimum_air_temp_nasa, max_air_temp_nasa,wind_speed_nasa,solar_radiation_nasa, RH_nasa, total_rain_nasa, snow_depth_nasa))
    db.commit()

def add_soil_data(table_name, date, column_name, soil_temp):
    sql = "INSERT INTO `{}`(date, {}) VALUES (%s, %s)" \
          "ON DUPLICATE KEY UPDATE  {}=values({})".format(table_name, column_name, column_name, column_name)
    cursor.execute(sql, (date, soil_temp))
    db.commit()

def add_snow_calibration_nse(table_name, sno_vals,sno_vals_col, nse_value, nse_col):
    sql = "INSERT INTO `{}`({}, {}) VALUES (%s, %s)" \
          "ON DUPLICATE KEY UPDATE  {}=values({}), {}=values({})".\
        format(table_name, sno_vals_col, nse_col, sno_vals_col, sno_vals_col, nse_col, nse_col)
    cursor.execute(sql, (sno_vals, nse_value))
    db.commit()

def add_cweeds_data(table_name, date, cweeds_diffuse_horizontal):
    sql = "INSERT INTO `{}`(date, cweeds_diffuse_horizontal) VALUES (%s, %s)" \
          "ON DUPLICATE KEY UPDATE  cweeds_diffuse_horizontal=values(cweeds_diffuse_horizontal)".format(table_name)
    cursor.execute(sql, (date, cweeds_diffuse_horizontal))
    db.commit()

def add_adjusted_total_rain(table_name, date, total_rain_adjusted):
    sql = "INSERT INTO `{}`(date, total_rain_adjusted) VALUES (%s, %s)" \
          "ON DUPLICATE KEY UPDATE  total_rain_adjusted=values(total_rain_adjusted)".format(table_name)
    cursor.execute(sql, (date, total_rain_adjusted))
    db.commit()
#####select action
def select_dl_eccc_data(year, station_id):
    try:
        sql = "SELECT `file_location` FROM `downloaded_eccc_data` WHERE station_id = ('{}') AND year = ('{}')".format(station_id, year)
        #print(sql)
        cursor.execute(sql)
        result = cursor.fetchone()
        return result
    except Exception as e:
        print(e)

def select_all_from_a_col(col, station):
    try:
        sql = "SELECT `{}` FROM `{}`".format(col, station)
        #print(sql)
        cursor.execute(sql)
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(e)

def select_one_value_from_a_col_with_condition(col_to_choose, table_name, col_condition, condition_value):
    try:
        sql = "SELECT `{}` FROM `{}` WHERE `{}` = '{}'".format(col_to_choose, table_name, col_condition, condition_value)
        cursor.execute(sql)
        result = cursor.fetchone()
        return result
    except Exception as e:
        print(e)

def select_one_col_with_highest_value(col_name, table_name, column_to_be_selected):
    try:
        sql = "SELECT {} FROM {} WHERE {} = (SELECT MAX({}) FROM {})".format(column_to_be_selected,
                                                                             table_name, col_name, col_name, table_name)
        # print(sql)
        cursor.execute(sql)
        result = cursor.fetchone()
        return result
    except Exception as e:
        print(e)


def select_multiple_col_based_on_date_range(start, end,table_name, col_to_choose):
    try:
        sql = "SELECT {} FROM `{}` WHERE `date` BETWEEN '{}' and '{}'".format(col_to_choose, table_name, start, end)
        cursor.execute(sql)
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(e)

def check_if_a_value_exists_in_a_column(table_name, column_name, value):
    try:
        sql = "SELECT * FROM `{}` WHERE {} = '{}'".format(table_name, column_name, value)
        cursor.execute(sql)
        result = cursor.fetchone()
        return  result

    except Exception as e:
        print(e)



####create table
def create_table(Table,table_name, DB_name, the_cursor):
    the_cursor.execute("USE {}".format(DB_name))
    table_description = Table
    try:
            # print(table_description)
            print("creating table ({})".format(table_name), end="")
            the_cursor.execute(table_description)
    except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("Table alreayd exists")
            else:
                print(err.msg)

####change datatype
def change_data_type_for_a_column(station, column, change_to):
        sql = "ALTER TABLE `ca_freeze_thaw`.`{}`MODIFY COLUMN `{}` {};".format(station, column, change_to)
        cursor.execute(sql)
        db.commit()

def change_primary_key_for_a_column(station, column):
    sql = "ALTER TABLE {} MODIFY `id` INT,  DROP PRIMARY KEY, ADD PRIMARY KEY({})".format(station, column)
    cursor.execute(sql)
    db.commit()

def drop_a_column(station, column):
    sql = "ALTER TABLE {} DROP COLUMN {};".format(station, column)
    cursor.execute(sql)
    db.commit()

def rename_a_column(station,column, new_column_name):
    sql = 'ALTER TABLE {} RENAME COLUMN {} TO {}'.format(station, column, new_column_name)
    print(sql)
    cursor.execute(sql)
    db.commit()

####add column to the existing table
def add_column_to_existing_table(table_name, column_name, data_type):
    sql = "ALTER TABLE ca_freeze_thaw.{} ADD {} {}".format(table_name, column_name, data_type)
    cursor.execute(sql)
    db.commit()

######add delete action
def add_downloaded_data(file_name, file_location, station_id, year):
    sql = "INSERT INTO `downloaded_eccc_data`(file_name, file_location, station_id, year) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, (file_name, file_location, station_id, year))
    db.commit()
    id = cursor.lastrowid
    print("Added element{}".format(id))

def add_snow_test_res(avg_snow, init_snow, nse):
    sql = "INSERT INTO `snow_sobol_test`(avg_snow, init_snow, nse) VALUES (%s, %s, %s)"
    cursor.execute(sql, (avg_snow, init_snow, nse))
    db.commit()
    id = cursor.lastrowid
    print("Added element{}".format(id))

#####select action
def select_dl_eccc_data(year, station_id):
    try:
        sql = "SELECT `file_location` FROM `downloaded_eccc_data` WHERE station_id = ('{}') AND year = ('{}')".format(station_id, year)
        #print(sql)
        cursor.execute(sql)
        result = cursor.fetchone()
        return result
    except Exception as e:
        print(e)




