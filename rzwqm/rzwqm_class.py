from datetime import datetime, timedelta
import os

class RZWQM:

    def __init__(self, met_path, brk_path, simulate_path, rzwqm_project_path=None):
        self.met_path = met_path
        self.brk_path = brk_path
        self.rzwqm_project_path = rzwqm_project_path
        self.simulate_path = simulate_path

    def rzwqm_res_parse(self, var_name):
        # this function is to parse the rzwqm result, and return only the required column as list
        # should have a list for corresponding var's column number
        # for snow, it should be 91
        if var_name == 'snow':
            column_num = 91
        julien_day_col = 0
        lines = read_text_file(self.simulate_path)
        del lines[0]
        # result starts at index #23
        lines = lines[23:]
        desired_data = {}
        for line in lines:
            try:
                desired_data[datetime.strptime(line[julien_day_col], '%Y.%j')] = float((line[column_num]))
            except Exception as e:
                print(e)
                year = line[julien_day_col].split('.')[0]
                desired_data[datetime.strptime(year+ '.' +'001', '%j%Y')] = float(
                    (line[column_num]))
        return desired_data

    def rzwqm_met_parse(self):
        # this function parses the met file
        with open(self.met_path) as f:
            lines = [line.rstrip('\n') for line in f]
        head = lines[0:36]
        content = lines[36:]
        parsed_content = []
        for line in content:
            split_line = line.split()
            parsed_content.append(split_line)
        return {'head': head, 'parsed_content': parsed_content}

    def write_to_rzwqm_met(self, name, parsed_content, head):
        to_write = []
        for line in parsed_content:
            s = f"   {line[0]}   {line[1]}   {line[2]}   {line[3]}   {line[4]}   {line[5]}   {line[6]}   {line[7]}   {line[8]}    {line[9]}"
            to_write.append(s)
        head.extend(to_write)
        with open(name, 'w') as file:
            for line in head:
                file.write(line + '\n')

    def rzwqm_met_modify(self, new_var_list, parsed_content):
        new_met_now = parsed_content['parsed_content']
        for data in new_var_list:
            for count, og_data in enumerate(new_met_now):
                fmt = '%Y%j'
                jdate = og_data[1] + og_data[0]
                og_date = datetime.strptime(jdate, fmt)
                if data['date'].date() == og_date.date():
                    if float(new_met_now[count][9]) == 0:
                        # print(f"new rain is {data['new_value']}, and old rain is {new_met_now[count][9]}")
                        new_met_now[count][9] = data['new_value']
                        break
        parsed_content['parsed_content'] = new_met_now
        return parsed_content

    def rzwqm_general_text_parse(self, out_file_name, head_end):
        path = os.path.join(self.rzwqm_project_path, out_file_name)
        with open(path) as f:
            lines = [line.rstrip('\n') for line in f]
        head = lines[0:head_end]
        content = lines[head_end:]
        parsed_content = []
        for line in content:
            split_line = line.split()
            parsed_content.append(split_line)
        return {'head': head, 'parsed_content': parsed_content}

    @staticmethod
    def change_param_val_in_one_line(columns_with_val, line):
        changed = line.split()
        for val in columns_with_val.keys():
            changed[val] = columns_with_val[val]
        return changed

    @staticmethod
    def rzwqm_parse_layer(desired_depth, layer_content):
        return_obj = {}
        for data in layer_content:
            if int(data[1]) in desired_depth:
                if return_obj[int(data[1])]:
                    return_obj[int(data[1])].append(data)
            else:
                return_obj[int(data[1])] = []
                return_obj[int(data[1])].append(data)
        return return_obj

    @staticmethod
    def return_layer_date_count(start, end, month_s, month_e, fmt, start_day):
        # start day is whether the date for the project starts from julien day in the first year
        dates = {}
        s = datetime.strptime(start, fmt)
        e = datetime.strptime(end, fmt)
        length = abs((s - e).days)
        for val in range(length + 1):
            # day = s + timedelta(days=val+1)
            # from the range between the two dates, start with the start date, store to the list
            day = s + timedelta(days=val)
            if day.month >= month_s or day.month <= month_e:
                c = val + start_day
                dates[c] = day
        return dates

    @staticmethod
    def return_dates_within_range(start, end, fmt):
        sdate = datetime.strptime(start, fmt)  # start date
        edate = datetime.strptime(end, fmt)  # end date
        date_modified = sdate
        return_list = [sdate]

        while date_modified < edate:
            date_modified += timedelta(days=1)
            return_list.append(date_modified)

        return return_list
    @staticmethod
    # create N number of instance for the RZ-SHAW, the if_snow represents whether the snow is being calibrated
    def create_rz_shaw_instance(original_instance_project_path, number_of_instance_to_create, original_instance_name,
                                if_snow):
        number_list = list(range(1, number_of_instance_to_create + 1))
        for number in number_list:
            # create instance
            new_instance_name = original_instance_name + str(number)
            src = original_instance_project_path + original_instance_name
            dst = original_instance_project_path + new_instance_name
            copytree(src, dst)

            # change ipnames for the instance
            rz = RZWQM(original_instance_project_path, new_instance_name)
            ip = rz.ipnames
            ip[0] = original_instance_project_path + new_instance_name + "\\cntrl.dat"
            ip[1] = original_instance_project_path + new_instance_name + "\\rzwqm.dat"
            ip[4] = original_instance_project_path + new_instance_name + "\\rzinit.dat"
            ip[5] = original_instance_project_path + new_instance_name + "\\plgen.dat"
            if if_snow:
                src_sno_file = original_instance_project_path + 'Meteorology\\' + original_instance_name + '.sno'
                dst_snow_file = original_instance_project_path + 'Meteorology\\' + new_instance_name + '.sno'
                shutil.copyfile(src_sno_file, dst_snow_file)
                ip[6] = original_instance_project_path + 'Meteorology\\' + new_instance_name + '.sno'
            ip[7] = original_instance_project_path + "Analysis" + "\\" + new_instance_name + ".ana"
            with open(rz.ipnames_path, 'w') as file:
                for line in ip:
                    file.write(line + '\n')
            print(new_instance_name + ' ' + 'created')
