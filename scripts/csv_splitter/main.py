#!/usr/bin/env python3
import csv
import json
import os
import sys
import statistics
from datetime import datetime
STATION_URIS_FILE = "../station_uris/station_to_uri.json"
DATA_SET_FILE = "../spreadsheets/complete.csv"
DATETIME_PARSING_STRING = "%Y-%m-%d %H:%M:%S"
DATE_PARSING_STRING = "%Y-%m-%d"
DIRECTORY_STRING = "results/{}"
FILE_STRING = "results/{}/{}{}.csv"
CSV_ENTRY_STRING = "http://irail.be/vehicle/{}{},{},{},{},{},{},{}\n"

class Main:
    def __init__(self):
        # Read station URI mapping
        self.station_uri_mapping = None
        with open(STATION_URIS_FILE) as jsonfile:
            self.station_uri_mapping = json.load(jsonfile)

    def split_data(self):
        with open(DATA_SET_FILE) as csvfile:
            reader = csv.reader(csvfile)
            for index, row in enumerate(reader):
                # Unpack row
                date, train_no, relation, operator, ptcar_no, line_no_dep,\
                real_time_arr, real_time_dep, planned_time_arr,\
                planned_time_dep, delay_arr, delay_dep, relation_direction,\
                ptca_lg_nm_nl, line_no_arr, planned_date_arr, planned_date_dep,\
                real_date_arr, real_date_dep = row

                # Handle vehicle type
                vehicle_type = None
                if "ICE" in relation:
                    vehicle_type = "ICE"
                elif "THAL" in relation:
                    vehicle_type = "THA"
                elif "TGV" in relation:
                    vehicle_type = "TGV"
                elif "IC/L" in relation:
                    vehicle_type = "IC_L"
                elif "EURST" in relation:
                    vehcile_type = "EUR"
                elif "LR_HKV" in relation:
                    vehicle_type = "LR_HKV"
                elif "LR_HST" in relation:
                    vehicle_type = "LR_HST"
                elif "CHARTER" in relation:
                    vehicle_type = "CHARTER"
                elif "IZY" in relation:
                    vehicle_type = "IZY"
                elif "INT" in relation:
                    vehicle_type = "INT"
                elif "ICT" in relation:
                    vehicle_type = "IC"
                elif "IC" in relation:
                    vehicle_type = "IC"
                elif "L" in relation:
                    vehicle_type = "L"
                elif "S" in relation:
                    # Make sure we have S1/S5/S6/... instead of S only
                    vehicle_type = relation.split("-")[0]
                elif "P" in relation:
                    vehicle_type = "P"
                else:
                    # Skip all other trains
                    continue

                # Exception flags
                is_departure_stop = False
                is_arrival_stop = False

                # Parse the departure date and time
                try:
                    planned_dep = datetime.strptime("{} {}"\
                            .format(planned_date_dep, planned_time_dep),
                            DATETIME_PARSING_STRING)
                except ValueError:
                    is_departure_stop = True

                # Parse the arrival date and time
                try:
                    planned_arr = datetime.strptime("{} {}"\
                            .format(planned_date_arr, planned_time_arr),
                            DATETIME_PARSING_STRING)
                except ValueError:
                    is_arrival_stop = True

                # Insert additional timestamps for departure and arrival stop
                # of vehicles
                if is_departure_stop:
                    planned_dep = planned_arr

                if is_arrival_stop:
                    planned_arr = planned_dep

                # Convert stop name to iRail station URI
                stop_uri = self.station_uri_mapping.get(ptca_lg_nm_nl.lower(), "NO-URI")

                # Entry date conversion
                entry_date = datetime.strptime(date, DATE_PARSING_STRING)
                directory = DIRECTORY_STRING.format(entry_date.year)
                if not os.path.exists(directory):
                    os.makedirs(directory)

                # Write entries to CSV
                with open(FILE_STRING.format(entry_date.year, vehicle_type, train_no), "a") as f:
                    f.write(CSV_ENTRY_STRING.format(vehicle_type,
                                                    train_no,
                                                    stop_uri,
                                                    vehicle_type,
                                                    planned_dep.isoformat(),
                                                    planned_arr.isoformat(),
                                                    delay_dep,
                                                    delay_arr))
                # Show progress
                sys.stdout.write("\rRow: {}".format(index))
                sys.stdout.flush()

    def execute_statistics(self):
        for year in os.listdir("results"):
            for index, vehicle in enumerate(os.listdir("results/{}".format(year))):
                stop_delays = {}

                # Skip JSON files
                if "json" in vehicle:
                    continue

                # Process each CSV
                with open("results/{}/{}".format(year, vehicle)) as csvfile:
                    reader = csv.reader(csvfile)
                    for index, row in enumerate(reader):
                        # Unpack row
                        try:
                            vehicle_uri, stop, vehicle_type, planned_dep,\
                            planned_arr, delay_dep, delay_arr = row
                        except ValueError:
                            print(row)
                            raise ValueError()

                        if "NO-URI" in stop:
                            continue

                        # Add entry if needed
                        if stop not in stop_delays:
                            stop_delays[stop] = {
                                "departure": {
                                    "median" : 0.0,
                                    "mean": 0.0,
                                    "variance": 0.0,
                                    "min": 0.0,
                                    "max": 0.0,
                                    "raw": []
                                    },
                                "arrival":{
                                    "median" : 0.0,
                                    "mean": 0.0,
                                    "variance": 0.0,
                                    "min": 0.0,
                                    "max": 0.0,
                                    "raw": []
                                    }
                                }

                        if delay_dep != "":
                            stop_delays[stop]["departure"]["raw"].append(int(delay_dep))

                        if delay_arr != "":
                            stop_delays[stop]["arrival"]["raw"].append(int(delay_arr))

                for stop in stop_delays:
                    if len(stop_delays[stop]["departure"]["raw"]) >= 2:
                        stop_delays[stop]["departure"]["min"] = min(stop_delays[stop]["departure"]["raw"])
                        stop_delays[stop]["departure"]["max"] = max(stop_delays[stop]["departure"]["raw"])
                        stop_delays[stop]["departure"]["mean"] = statistics.mean(stop_delays[stop]["departure"]["raw"])
                        stop_delays[stop]["departure"]["median"] = statistics.median(stop_delays[stop]["departure"]["raw"])
                        stop_delays[stop]["departure"]["variance"] = statistics.variance(stop_delays[stop]["departure"]["raw"])

                    if len(stop_delays[stop]["arrival"]["raw"]) >= 2:
                        stop_delays[stop]["arrival"]["min"] = min(stop_delays[stop]["arrival"]["raw"])
                        stop_delays[stop]["arrival"]["max"] = max(stop_delays[stop]["arrival"]["raw"])
                        stop_delays[stop]["arrival"]["mean"] = statistics.mean(stop_delays[stop]["arrival"]["raw"])
                        stop_delays[stop]["arrival"]["median"] = statistics.median(stop_delays[stop]["arrival"]["raw"])
                        stop_delays[stop]["arrival"]["variance"] = statistics.variance(stop_delays[stop]["arrival"]["raw"])

                with open("results/{}/{}.json".format(year, vehicle.split(".")[0]), "w") as jsonfile:
                    json.dump(stop_delays, jsonfile, indent=4)

                # Show progress
                sys.stdout.write("\r{}: {}".format(year, index))
                sys.stdout.flush()


if __name__ == "__main__":
    m = Main()
    m.split_data()
    m.execute_statistics()

