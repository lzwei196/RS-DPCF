from env_var_fun import read_csv_line_by_line, read_json
import geopy.distance
from pprint import pprint
soil_type_db = read_csv_line_by_line('info.csv')
del soil_type_db[0]
checked_stations = read_json('checked_with_dlyandhly.json')
soil_type_dict = {}

for station in soil_type_db:
    station_id = station[3]
    temp_dict = {}
    temp_dict['cord'] = [float(station[-2]), float(station[-1])]
    temp_dict['soil type']= station[10] + ' ' + station[11] + ' ' + station[12]
    soil_type_dict[station_id] = temp_dict

for checked_station in checked_stations:
    current_station_cords = [checked_stations[checked_station]['loc'][1], checked_stations[checked_station]['loc'][0]]
    shortest_dis = 1000
    closest_station = ''
    for station in soil_type_dict:
        cord = soil_type_dict[station]['cord']
        dis = geopy.distance.geodesic(current_station_cords, cord).km
        if dis < shortest_dis:
            shortest_dis = dis
            closest_station = station