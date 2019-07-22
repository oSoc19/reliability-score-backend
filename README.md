# Reliability Score backend

The backend is running on a Herokuapp Free Dyno at: [https://reliability-score.herokuapp.com/](https://reliability-score.herokuapp.com)
:warning: When the backend is down (free plan, after 1 hour of inactivity), you need to wait until the Dyno is ready.
This process doesn't take longer than 20 seconds.

TODO: explain project

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

## Machine Learning


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
