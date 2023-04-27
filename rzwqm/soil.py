import matplotlib as mpl
from rzwqm.rzwqm_file_fun import return_layer_date_count

mpl.use('TkAgg')


def rzwqm_parse_layer(desired_depth, path, head_end, column_num):
    #desired_dates = return_layer_date_count('2000-01-01', '2005-12-31', 11, 4, '%Y-%m-%d')
    with open(path) as f:
        lines = [line.rstrip('\n') for line in f]
    head = lines[0:head_end]
    content = lines[head_end:]
    parsed_content = []
    for line in content:
        split_line = line.split()
        parsed_content.append(split_line)
    return_obj = {}
    for data in parsed_content:
      the_depth = int(float(data[1]))
      if the_depth in desired_depth:
           try:
              if return_obj[the_depth]:
                  return_obj[the_depth].append(float(data[column_num]))
           except Exception as e:
              return_obj[the_depth] = []
              return_obj[the_depth].append(float(data[column_num]))

    return return_obj


def parse_ob_soil_temp(available_depth, path):
    ob_soil = read_the_file_split(path)
    del ob_soil[0]
    soil_temp = {}
    for temp in available_depth.keys():
        soil_temp[temp] = []
    for data in ob_soil:
        for val in available_depth:
            soil_temp[val].append(float(data[available_depth[val]]))
    return soil_temp

def return_desired_ob_soil_temp(ob_data, desired_dates, start_day):
    desired_data = {}
    for key in ob_data:
        desired_data[key] = []
        for count, line in enumerate(ob_data[key]):
            count = count + start_day
            if count in desired_dates:
                desired_data[key].append(line)
    return desired_data

def return_desired_sim_data(sim_data, desired_dates, start_day):
    desired_data = []
    counts = desired_dates.keys()
    for count, val in enumerate(sim_data):
        if count - start_day +1 in counts:
            desired_data.append(val)

    return desired_data

