import mysql.connector
from mysql.connector import errorcode
from db_connection import cursor
from db_functions import read_jsonfile

Table = {}

###table information
Table['env_elements'] = (
    "CREATE TABLE `Env Variables`("
    "`element_id` int(11) NOT NULL AUTO_INCREMENT,"
    "`element_code` varchar(250) NOT NULL,"
    "`variable_name` varchar(250) NOT NULL,"
    "PRIMARY KEY (`element_id`)"
    ")  ENGINE=InnoDB"
)

Table['station_data_years'] = (
    "CREATE TABLE `station_data_years`("
    "`id` int(11) NOT NULL  AUTO_INCREMENT,"
    "`station_id` TEXT NOT NULL,"
    "`first_year` int(4) NOT NULL,"
    "`last_year` int(4) NOT NULL,"
    "`hly_first_year` int(4),"
    "`hly_last_year` int(4),"
    "`dly_first_year` int(4),"
    "`dly_last_year` int(4),"
    "`mly_first_year` int(4),"
    "`mly_last_year` int(4),"
    "PRIMARY KEY (`id`)"
    ")ENGINE=InnoDB"
)

Table['years_for_each_element'] = (
    "CREATE TABLE `years_for_each_element`("
    "`year_id` int(11) NOT NULL AUTO_INCREMENT,"
    "`element_id` int(11) NOT NULL ,"
    "`year` int(4) NOT NULL ,"
    "PRIMARY KEY (`year_id`),"
    "FOREIGN KEY(`element_id`) REFERENCES `env variables`(element_id)"
    ")ENGINE=InnoDB"
)

Table['dly_date_data'] = (
    "CREATE TABLE `env_dly_date_data`("
    "`date_data_id` int(11) NOT NULL AUTO_INCREMENT,"
    "`year_id` int(11) NOT NULL,"
    "`station_id` VARCHAR(7) NOT NULL,"
    "`elementnum` CHAR(3) NOT NULL,"
    "`month` int(2) NOT NULL ,"
    "PRIMARY KEY (`date_data_id`),"
    "FOREIGN KEY(`year_id`) REFERENCES `years_for_each_element`(year_id)"
    ") ENGINE = InnoDB"
)

Table['station_id'] = (
    "CREATE TABLE `station_id`("
    "`id` int(11) NOT NULL AUTO_INCREMENT,"
    "`name` TEXT NOT NULL ,"
    "`province` TEXT NOT NULL ,"
    "`climate_id` TEXT NOT NULL,"
    "`station_id` TEXT NOT NULL,"
    "`latitude` DOUBLE NOT NULL ,"
    "`longitude` DOUBLE NOT NULL, "
    "`elevation` DOUBLE NOT NULL, "
    "PRIMARY KEY (`id`)"
    ") ENGINE = InnoDB"
)

Table['downloaded_eccc_data'] = (
    "CREATE TABLE `downloaded_eccc_data`("
    "`id` int(11) NOT NULL AUTO_INCREMENT,"
    "`file_name` LONGTEXT NOT NULL,"
    "`file_location` LONGTEXT NOT NULL ,"
    "`station_id` TEXT NOT NULL ,"
    "`year` int(4) NOT NULL ,"
    "PRIMARY KEY (`id`))"
    "ENGINE =InnoDB"
)

Table['snow_sobol_test'] = (
    "CREATE TABLE `snow_sobol_test`("
    "`id` int(11) NOT NULL AUTO_INCREMENT,"
    "`avg_snow` float NOT NULL ,"
    "`init_snow` float NOT NULL ,"
    "`NSE` float NOT NULL ,"
    "PRIMARY KEY (`id`))"
    "ENGINE =InnoDB"
)


def station_observed_data_table(name, soil_temp_keys):
    sql_soil = ""
    for depth in soil_temp_keys:
        sql_soil = sql_soil + "`soil_temp_" + depth + "`" + " DOUBLE(11,2),"
    sql = (
        "CREATE TABLE `{}`""(`date` VARCHAR(11) UNIQUE,"
        "`minimum_air_temp` DOUBLE(11,2),"
        "`minimum_air_temp_nasa` DOUBLE(11,2),"
        "`max_air_temp` DOUBLE(11,2),"
        "`max_air_temp_nasa` DOUBLE(11,2),"
        "`RH` DOUBLE(11,2),"
        "`RH_nasa` DOUBLE(11,2),"
        "`wind_speed` DOUBLE(11,2),"
        "`wind_speed_nasa` DOUBLE(11,2),"
        "`solar_radiation` DOUBLE(11,2),"
        "`solar_radiation_nasa` DOUBLE(11,2),"
        "`total_rain_adjusted` DOUBLE(11,2),"
        "`total_rain_nasa` DOUBLE(11,2),"
        "`snow_depth_adjusted` DOUBLE(11,2),"
        "`snow_depth_nasa` DOUBLE(11,2), "
        "{}"
        "PRIMARY KEY (`date`))""ENGINE = InnoDB".format(name, sql_soil)
    )
    return sql


def db_dly_date_data(name):
    sql = (
        "CREATE TABLE `{}`("
        "`date_data_id` int(11) NOT NULL AUTO_INCREMENT,"
        "`year_id` int(11) NOT NULL,"
        "`station_id` TEXT NOT NULL,"
        "`elementnum` CHAR(3) NOT NULL,"
        "`month` int(2) NOT NULL ,"
        "PRIMARY KEY (`date_data_id`),"
        "FOREIGN KEY(`year_id`) REFERENCES `years_for_each_element`(year_id)"
        ") ENGINE = InnoDB".format(name)
    )
    return sql


def db_dly_value(name):
    sql = (
        "CREATE TABLE `{}`("
        "`data_id` int(11) NOT NULL AUTO_INCREMENT,"
        "`date_data_id` int(11) NOT NULL,"
        "`dayinthemonth` int(2) NOT NULL,"
        "`value` LONGTEXT NOT NULL ,"
        "PRIMARY KEY (`data_id`),"
        "FOREIGN KEY(`date_data_id`) REFERENCES `{}`(`date_data_id`)"
        ")ENGINE = InnoDB".format(name, name + "_date_id")
    )
    return sql


def station_observed_data_table(name, soil_temp_keys):
    sql_soil = ""
    for depth in soil_temp_keys:
        sql_soil = sql_soil + "`soil_temp_" + depth + "`" + " DOUBLE(11,2),"
    sql = (
        "CREATE TABLE `{}`""(`date` VARCHAR(11) UNIQUE,"
        "`minimum_air_temp` DOUBLE(11,2),"
        "`minimum_air_temp_nasa` DOUBLE(11,2),"
        "`max_air_temp` DOUBLE(11,2),"
        "`max_air_temp_nasa` DOUBLE(11,2),"
        "`RH` DOUBLE(11,2),"
        "`RH_nasa` DOUBLE(11,2),"
        "`wind_speed` DOUBLE(11,2),"
        "`wind_speed_nasa` DOUBLE(11,2),"
        "`solar_radiation` DOUBLE(11,2),"
        "`solar_radiation_nasa` DOUBLE(11,2),"
        "`total_rain_adjusted` DOUBLE(11,2),"
        "`total_rain_nasa` DOUBLE(11,2),"
        "`snow_depth_adjusted` DOUBLE(11,2),"
        "`snow_depth_nasa` DOUBLE(11,2), "
        "{}"
        "PRIMARY KEY (`date`))""ENGINE = InnoDB".format(name, sql_soil)
    )
    return sql


def add_snow_cali_table(name, soil_temp_keys):
    sql_soil = ""
    if soil_temp_keys:
        for depth in soil_temp_keys:
            sql_soil = sql_soil + "`soil_temp_" + depth + "`" + "JSON,"
            sql_soil = sql_soil + "`soil_temp_" + depth + "NSE`" + "DOUBLE(11,2),"
            sql_soil = sql_soil + "`soil_temp_" + depth + "MBE`" + "DOUBLE(11,2),"
            sql_soil = sql_soil + "`soil_temp_" + depth + "RMSD`" + "DOUBLE(11,2),"
            sql_soil = sql_soil + "`soil_temp_" + depth + "IOA`" + "DOUBLE(11,2),"
            sql_soil = sql_soil + "`soil_temp_" + depth + "R2`" + "DOUBLE(11,2),"
    sql = (
        "CREATE TABLE `{}`""(`the_id` INT UNIQUE NOT NULL auto_increment,"
        "`snow_rho_ini, snow_rho max` varchar(15),"
        "`NSE` DOUBLE(11,2),"
        "`MBE` DOUBLE(11,2),"
        "`RMSD` DOUBLE(11,2),"
        "`snow_data` JSON,"
        "{}"
        "PRIMARY KEY (`snow_rho_ini, snow_rho max`))""ENGINE = InnoDB".format(name, sql_soil)
    )
    cursor.execute(sql)
    db.commit()


def create_db(DB_name):
    cursor.execute("CREATE DATABASE IF NOT EXISTS {} DEFAULT CHARACTER SET 'UTF8'".format(DB_name))
    print('database {} created!'.format(DB_name))


def create_var(paths, table):
    vars = read_jsonfile(paths)
    for key, val in vars.items():
        td = db_dly_date_data(key + "_date_id")
        t = db_dly_value(key)
        table[key + "_date_id"] = td
        table[key] = t
    return table


def create_tables(Table, DB_name, the_cursor):
    the_cursor.execute("USE {}".format(DB_name))
    gened_Table = create_var('', Table)
    for table_name in gened_Table:
        table_description = gened_Table[table_name]
        try:
            # print(table_description)
            print("creating table ({})".format(table_name), end="")
            the_cursor.execute(table_description)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("Table alreayd exists")
            else:
                print(err.msg)


