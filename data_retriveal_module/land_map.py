for year in land_areas:
    for station in land_areas[year]:
        the_station_id = list(station.keys())[0]
        if the_station_id not in list(new_dict.keys()):
            new_dict[the_station_id] = station[the_station_id]
        else:
            new_dict[the_station_id]['frequency'].update(station[the_station_id]['frequency'])

for station in new_dict:
    temp_dict = {}
    for land_cover in new_dict[station]['frequency']:
        if int(land_cover) <= 34 or int(land_cover) >= 199:
            pass
        else:
            temp_dict[land_cover] =  new_dict[station]['frequency'][land_cover]
    new_dict[station]['frequency'] = temp_dict

    new_dict[station]['crop'] = inventory_code[(max(new_dict[station]['frequency'], key=new_dict[station]['frequency'].get))]

with open('final_stations_list.json', 'w') as file:
    json.dump(new_dict, file)

