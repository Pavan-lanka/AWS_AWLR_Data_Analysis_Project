import warnings

from st_plot import StationModelPlot
import cv2


def main():
    obtain_method = {'fetch_data': 'Enter Valid Station ID to fetch data:\t',
                     'upload_data_file': 'Enter Path to file or File as object:\t'
                     }
    abbreviations = {
        'date_time': ['valid', 'time', 'date_time', 'time1', 'time_stamp', 'DATE_TIME'],
        'pressure': ['PRESSURE', 'pres', 'mslp', 'atmospheric_pressure', 'air_pressure_at_sea_level'],
        'present_weather': ['coco', 'current_weather', 'wxcodes', 'current_wx1', 'current_wx1_symbol',
                            'present_weather']
    }
    meteostat_weather_code_map = {1: 0,
                                  2: 0,
                                  3: 0,
                                  4: 0,
                                  5: 45,
                                  6: 49,
                                  7: 61,
                                  8: 63,
                                  9: 65,
                                  10: 66,
                                  11: 67,
                                  12: 68,
                                  13: 69,
                                  14: 71,
                                  15: 73,
                                  16: 75,
                                  17: 80,
                                  18: 81,
                                  19: 0,
                                  20: 0,
                                  21: 85,
                                  22: 86,
                                  23: 0,
                                  24: 90,
                                  25: 17,
                                  26: 97,
                                  27: 31
                                  }
    while True:
        ip = input(
            f'''Enter a method from below: \n {list(obtain_method.keys())[0]}:(f), {list(obtain_method.keys())[1]}(u):\n''')
        if ip.lower() == 'f':
            st_id = input(obtain_method['fetch_data'])
            st = StationModelPlot(station_id=st_id)
            st_time = StationModelPlot.get_time_stamp(
                input("Enter End time in format: 'YYYY-MM-DD HH:MM:SS ex. 2022-01-10 00:00:00 --:\n"))
            ed_time = StationModelPlot.get_time_stamp(
                input("Enter End time in format: 'YYYY-MM-DD HH:MM:SS ex. 2022-01-20 00:00:00 --:\n"))
            freq = input("Enter observation Frequency from list [Hourly, Daily] : \t")
            try:
                fetched_data, fetched_data_columns = st.fetch_station_data(start_time=st_time,
                                                                           end_time=ed_time,
                                                                           obs_frequency=freq)
                fetched_data = fetched_data.fillna('')
            except Exception as e:
                print('Please Enter Valid Station ID , Valid Start time and End time in format: YYYY-MM-DD HH:MM:SS')
                continue
        elif ip.lower() == 'u':
            pt_to_file = input(obtain_method['upload_data_file'])
            try:
                st = StationModelPlot(path_to_file=pt_to_file)
                fetched_data, fetched_data_columns = st.custom_file_read()
                fetched_data = fetched_data.fillna('')
            except Exception as e:
                print('Entered Path File is Incorrect please enter a valid file path, or file as an object')
                continue
        else:
            continue
        while True:
            try:
                for iteration2 in range(len(abbreviations['date_time'])):
                    ts_column = abbreviations['date_time'][iteration2]
                    if ts_column in fetched_data_columns:
                        ts_column_values = fetched_data[ts_column]
                        time_stamp = StationModelPlot.get_time_stamp(input(
                            f'Enter Time Stamp from {ts_column_values} in the format: "YYYY-MM-DD HH:MM:SS ex. 2022-01-10 00:00:00 --: \n'))
                        if len(ts_column_values) > 0 and isinstance(ts_column_values[0], str):
                            ts_data = fetched_data.loc[ts_column_values == str(time_stamp)]
                            idx = fetched_data.index[ts_column_values == str(time_stamp)].to_list()
                        elif len(ts_column_values) > 0:
                            ts_data = fetched_data.loc[ts_column_values == time_stamp]
                            idx = fetched_data.index[ts_column_values == time_stamp].to_list()
                        ts_data = ts_data.squeeze()
                        ts_data = ts_data.fillna('')
                        break
                pres_value_dict = dict()
                weather_3hrs_ago = None
                for iteration in abbreviations['pressure']:
                    # if iteration not in fetched_data_columns:
                    if iteration in fetched_data_columns:
                        loop = 3
                        while loop > 0:
                            if len(idx) > 0 and (idx[0] - loop) >= 0:
                                pres_value_dict[loop] = int(fetched_data[iteration][idx[0] - loop])
                                loop -= 1
                            else:
                                break
                for iteration1 in abbreviations['present_weather']:
                    # if iteration1 not in fetched_data_columns:
                    #     continue
                    if iteration1 in fetched_data_columns:
                        if len(idx) > 0 and (idx[0] - 3) >= 0:
                            weather_3hrs_ago = fetched_data[iteration1][idx[0] - 3]
                        else:
                            weather_3hrs_ago = 0
            except Exception as e:
                print(e)
                continue
            plot_data = StationModelPlot.parameter_validation(ts_data, fetched_data_columns)
            pres_value_dict[0] = int(plot_data['pressure'])
            print(pres_value_dict)
            pres_values = StationModelPlot.press_values(pres_value_dict)
            if len(pres_values) == 3:
                if pres_values[0] != '':
                    plot_data['pressure_change'] = pres_values[0]
                if pres_values[1] != None:
                    plot_data['pressure_difference'] = pres_values[1]
                if pres_values[2] >= 0:
                    plot_data['pressure_tendency'] = pres_values[2]
                    print(plot_data['pressure_tendency'])
            elif len(pres_values) == 2:
                if pres_values[0] != '':
                    plot_data['pressure_change'] = pres_values[0]
                if pres_values[1] != None:
                    plot_data['pressure_difference'] = pres_values[1]
            plot_data['past_weather'] = weather_3hrs_ago
            if ip == 'f':
                plot_data['station_id'] = st_id
                meteo_weather_code = plot_data['present_weather'] if plot_data['present_weather'] >= 0 else 0
                if meteo_weather_code in meteostat_weather_code_map:
                    plot_data['present_weather'] = meteostat_weather_code_map[meteo_weather_code]
                    plot_data['past_weather'] = meteostat_weather_code_map[weather_3hrs_ago]
                    if meteo_weather_code == 0:
                        plot_data['present_weather'] = 0
                        raise warnings.warn(f"The Present Weather and Past Weather "
                                            "data is Inaccurate in Meteostat API for the current weather symbol")
            path = StationModelPlot.plot_station_model(data=plot_data)

            break
        break
    return path


if __name__ == '__main__':
    path_to_model = main()
    cv2.waitKey(10)
    img = cv2.imread(path_to_model)
    cv2.imshow('Station Model', img)
    key = cv2.waitKey(0)

    if key > -1 & 0xFF:
        cv2.destroyAllWindows()
