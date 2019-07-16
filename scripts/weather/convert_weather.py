#!/usr/bin/env python
import json
import requests
from statistics import mean

# Download URL for all Belgium weather data of KMI between 01/01/2016 and 16/07/2019
# 2016 is completely missing
METEO_DOWNLOAD_URL = 'https://opendata.meteo.be//download.php?workspace=aws&type=vector&layer=aws_1hour&format=json&bbox=50.193663,3.201846,51.347375,5.255236&time=2016-01-01T00:00:00Z/2019-07-16T15:00:00Z'

def parse(raw_data):
    data = {}

    # Extract the necessary data from the data set
    for entry in raw_data['features']:
        timestamp = entry['properties']['timestamp']
        if not timestamp in data:
            data[timestamp] = {
                'air_pressure': [],
                'air_temperature': [],
                'relative_humidity': [],
                'wind_speed': []
            }

        data[timestamp]['air_pressure'].append(entry['properties']['air_pressure'])
        data[timestamp]['air_temperature'].append(entry['properties']['air_temperature'])
        data[timestamp]['relative_humidity'].append(entry['properties']['relative_humidity'])
        data[timestamp]['wind_speed'].append(entry['properties']['wind_speed'])

    # Calculate mean values for the 2 measuring points
    for d in data:
        data[d]['air_pressure'] = mean(data[d]['air_pressure'])
        data[d]['air_temperature'] = mean(data[d]['air_temperature'])
        data[d]['relative_humidity'] = mean(data[d]['relative_humidity'])
        data[d]['wind_speed'] = mean(data[d]['wind_speed'])

    return data

def save(data):
    # AIR_PRESSURE, AIR_TEMPERATURE, RELATIVE_HUMIDITY, WIND_SPEED
    with open('weather-2016-2019.csv', 'w') as f:
        for d in data:
            f.write('{},{},{},{}\n'.format(data[d]['air_pressure'],
                                         data[d]['air_temperature'],
                                         data[d]['relative_humidity'],
                                         data[d]['wind_speed']))

if __name__ == '__main__':
    r = requests.get(METEO_DOWNLOAD_URL)
    data = parse(r.json())

    # Print results
    for d in data:
        print(d, data[d])

    # Save as CSV
    save(data)
