# Scrape updated CoVID data from https://www.stats.govt.nz/experimental/covid-19-data-portal
import requests
import pandas as pd
import pymysql
import calendar
from datetime import datetime

try:
    import config
except Exception:
    print("Please make config.py file and copy contents from dev info file")

current_time = datetime.now()

formatted_year = current_time.strftime("%Y")[2:]
formatted_time = (current_time.strftime("%d%b") + formatted_year).lower()

# Link to download .csv file, update link based on current data
url = 'https://www.health.govt.nz/system/files/documents/pages/covid-cases-' + \
    formatted_time + '.xlsx'


def download_data():
    data = requests.get(url, allow_redirects=True)

    open('covid_cases_{}.xlsx'.format(str(datetime.date(datetime.now()))),
         'wb').write(data.content)


def get_data():
    csv_file = pd.read_excel(r'covid_cases_{}.xlsx'.format(
        str(datetime.date(datetime.now()))), sheet_name="Confirmed", header=None)
    return csv_file.drop([0, 1, 2, 3])


def get_data_as_json():
    # Get formatted data as json
    data = get_data()
    json = [{
        "date": datetime.now(),
        "location": ""
    }]

    for row in data.iterrows():
        json.append({
            "date": row[1][0],
            "location": row[1][3]
        })

    # Filter past 20 days for active cases
    filtered_json = [
        x for x in json if (datetime.now() - x['date']).days <= 20
    ]

    # Get rid of null data
    filtered_json = [
        x for x in filtered_json if not x['location'] == "" and not x['location'] == 'Managed isolation & quarantine'
    ]

    return filtered_json


def parse_json():
    json = get_data_as_json()
    locs = {
        "": {
            "latitude": 0.0000,
            "longitude": 0.0000
        }
    }

    confirmed = [
        {
            "name": "",
            "latitude": 0.0000,
            "longitude": 0.0000,
            "confirmed": 0
        }
    ]

    # Map locs to lat, long
    with open("locations.txt") as locations:
        for line in locations:
            name, value = line.partition("=")[::2]
            # Change to langitude and longitude
            latitude, longitude = str(value).split(",")
            locs.update({
                name: {
                    "latitude": latitude,
                    "longitude": longitude.rstrip()
                }
            })
            confirmed.append({
                "name": name,
                "latitude": latitude,
                "longitude": longitude.rstrip(),
                "confirmed": 0
            })

    confirmed[0] = None
    for o in confirmed:
        if o is None:
            continue
        for object in json:
            # Increment confirmed
            if object["location"] == o["name"]:
                o["confirmed"] = o["confirmed"] + 1

    return confirmed


connection = pymysql.connect(
    host=config.host,
    user=config.username,
    password=config.password,
    port=config.port,
    database=config.database
)


def clear_data():
    connection.ping(reconnect=True)
    cursor = connection.cursor()
    query = "DELETE FROM covid_cases"
    try:
        cursor.execute(
            query)
        connection.commit()
    except Exception as e:
        print("Could not clear CoVID data, Error:", e)


def upload_data():
    json = parse_json()

    connection.ping(reconnect=True)
    cursor = connection.cursor()
    query = "INSERT INTO covid_cases (name, latitude, longitude, confirmed) VALUES (%s, %s, %s, %s)"
    for object in json:
        if object is None:
            continue
        try:
            cursor.execute(
                query, (object["name"], object["latitude"], object["longitude"], object["confirmed"]))
            connection.commit()
        except Exception as e:
            print("Could not update CoVID data, Error:", e)


# Update data in database
print("Downloading latest data as of " + '{}'.format(
    str(datetime.date(datetime.now()))))
download_data()
print("Uploading data into database")
clear_data()
upload_data()
print("Done.")
