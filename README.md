# Reliability Score backend

The backend is running on a Herokuapp Free Dyno at: [https://reliability-score.herokuapp.com/](https://reliability-score.herokuapp.com)

:warning: *When the backend is down (free plan, after 1 hour of inactivity), you need to wait until the Dyno is ready.
This process doesn't take longer than 20 seconds.*

The backend of Reliability Score project adds reliability information on top of the iRail API.
We use 4 years of historical delay information from Infrabel to determine the reliability of a train.
By performing statistics on the data, we can help commuters to plan their future journeys with the train.

## API

Our API uses the iRail API ([https://docs.irail.be](https://docs.irail.be/)) to provide clients the necessary routing information.
On top of this data, we use pre-generated JSON files which contain statistical information about a vehicle and the stations of its route.

This information is integrated into the API JSON data and used by our frontend application ([https://github.com/oSoc19/reliability-score-frontend](https://github.com/oSoc19/reliability-score-frontend)) to show how reliable your connection is.

### Resources

We have a single resource available at ´/connections?from={departureStation}&to={arrivalStation}&time={time}&date={date}&timesel={arrival or departure}´.
In comparison to the iRail API documentation, all of our arguments are required. In case an argument is missing, a `HTTP 400: Bad request` is returned.

- **from**: The name of the departure station, for example: `Vilvoorde`.
- **to**: The name of the arrival station, for example: `Brugge`.
- **time**: The time of the arrival or departure, for example: `0945` for 9h45 in the morning.
- **date**: The date of the arrival or departure, for example: `220719` for 22 Jul 2019.
- **timesel**: Use the provided `time` and `date` parameters as *to arrive at* or *to depart from*. The possible values are: `departure` or `arrival`.

### Example

**Request**: [https://reliability-score.herokuapp.com/connections?from=Diegem&to=Brugge&time=0851&date=220719&timesel=departure](https://reliability-score.herokuapp.com/connections?from=Diegem&to=Brugge&time=0851&date=220719&timesel=departure)

**Response**:

```json
{
    "version": "1.1",
    "timestamp": "1563787414",
    "connection": [
    {
      "id": "0",
      "departure": {
        "delay": "0",
        "station": "Diegem",
        "stationinfo": {
          "locationX": "4.442774",
          "locationY": "50.890478",
          "id": "BE.NMBS.008811213",
          "@id": "http://irail.be/stations/NMBS/008811213",
          "standardname": "Diegem",
          "name": "Diegem"
        },
        "time": "1563778260",
        "vehicle": "BE.NMBS.IC1930",
        "platform": "?",
        "platforminfo": {
          "name": "?",
          "normal": "1"
        },
        "canceled": "1",
        "departureConnection": "http://irail.be/connections/8811213/20190722/IC1930",
        "direction": {
          "name": "Tournai"
        },
        "left": "0",
        "walking": "0",
        "occupancy": {
          "@id": "http://api.irail.be/terms/unknown",
          "name": "unknown"
        },
        "reliability": {
          "0": 2.5,
          "1": 25.2,
          "2": 31.4,
          "3": 15.7,
          "4": 10.7,
          "5": 5.7,
          "6": 1.3,
          "7": 3.1,
          "8": 1.9,
          "9": 0.6,
          "10": 0.6,
          "11": 0,
          "12": 0,
          "13": 0,
          "14": 0,
          "15": 0,
          "16": 1.3
        }
      },
      "arrival": {
        "delay": "0",
        "station": "Brugge",
        "stationinfo": {
          "locationX": "3.216726",
          "locationY": "51.197226",
          "id": "BE.NMBS.008891009",
          "@id": "http://irail.be/stations/NMBS/008891009",
          "standardname": "Brugge",
          "name": "Brugge"
        },
        "time": "1563784140",
        "vehicle": "BE.NMBS.IC2830",
        "platform": "9",
        "platforminfo": {
          "name": "9",
          "normal": "1"
        },
        "canceled": "0",
        "direction": {
          "name": "Oostende"
        },
        "arrived": "0",
        "walking": "0",
        "reliability": {
          "0": 27.6,
          "1": 26.4,
          "2": 15.5,
          "3": 8.6,
          "4": 6.3,
          "5": 2.3,
          "6": 4,
          "7": 4,
          "8": 1.1,
          "9": 1.1,
          "10": 1.1,
          "11": 0.6,
          "12": 0,
          "13": 0,
          "14": 0,
          "15": 0,
          "16": 1.1
        }
      },
      "duration": "5880",
      "remarks": {
        "number": "2",
        "remark": [
          {
            "id": "0",
            "code": "SNCB_2090_HINT",
            "description": "The original, planned timetable of this trip has been replaced by a new one due to a redirection. Based upon the new timetable, the connection cannot be guaranteed. Consult the overview for an alternative trip."
          },
          {
            "id": "1",
            "code": "SNCB_2090_HINT",
            "description": "The original, planned timetable of this trip has been replaced by a new one due to a redirection. Based upon the new timetable, the connection cannot be guaranteed. Consult the overview for an alternative trip."
          }
        ]
      },
      "vias": {
        "number": "1",
        "via": [
          {
            "id": "0",
            "arrival": {
              "time": "1563779400",
              "platform": "15",
              "platforminfo": {
                "name": "15",
                "normal": "1"
              },
              "isExtraStop": "0",
              "delay": "0",
              "canceled": "0",
              "arrived": "0",
              "walking": "0",
              "direction": {
                "name": "Tournai"
              },
              "vehicle": "BE.NMBS.IC1930",
              "departureConnection": "http://irail.be/connections/8814001/20190722/IC1930"
            },
            "departure": {
              "time": "1563780480",
              "platform": "8",
              "platforminfo": {
                "name": "8",
                "normal": "1"
              },
              "isExtraStop": "0",
              "delay": "0",
              "canceled": "0",
              "left": "0",
              "walking": "0",
              "direction": {
                "name": "Oostende"
              },
              "vehicle": "BE.NMBS.IC2830",
              "departureConnection": "http://irail.be/connections/8814001/20190722/IC2830",
              "occupancy": {
                "@id": "http://api.irail.be/terms/unknown",
                "name": "unknown"
              }
            },
            "timeBetween": "1080",
            "station": "Brussels-South/Brussels-Midi",
            "stationinfo": {
              "locationX": "4.336531",
              "locationY": "50.835707",
              "id": "BE.NMBS.008814001",
              "@id": "http://irail.be/stations/NMBS/008814001",
              "name": "Brussels-South/Brussels-Midi",
              "standardname": "Brussel-Zuid/Bruxelles-Midi"
            },
            "vehicle": "BE.NMBS.IC1930",
            "direction": {
              "name": "Tournai"
            }
          }
        ]
      },
      "occupancy": {
        "@id": "http://api.irail.be/terms/unknown",
        "name": "unknown"
      }
    }
    ]
}
```

:bulb: *For example purposes, we only show a single route in this example above. In reality, several routes are returned by the backedn.*

## Machine Learning

TODO


## Scripts

In this projects, we use 3 different of scripts.
These scripts are used to parse and use the raw data from [https://infrabel.be](Infrabel).
The results of the scripts are available in the `data` folder.
The source code and documentation of these scripts can be found in the `scripts` folder.

### excel_to_csv

The first script `excel_to_csv` transforms the Excel files from Infrabel into an open format (CSV).
All the Excel files are converted to CSV files by date. The script also generates a single CSV file of the complete data set (`full.csv`)

### station_uris

The `station_uris` script allows us to match the Infrabel station names with the iRail station URIs.
Using this information, we can connect the Infrabel delay information with the right NMBS/SNCB station in the iRail API.

### csv_splitter

Our 3rd script `csv_splitter` splits the data into smaller pieces (CSV files) by year and vehicle ID.
After the splitting, we calculate the average delay, median delay and the variance using the Infrabel data.
This information is stored in a JSON file and used directly by the API.
