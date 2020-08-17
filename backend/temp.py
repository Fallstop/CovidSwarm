import pandas as pd
import pymysql
import random

try:
    import config
except Exception:
    print("Please make config.py file and copy contents from dev info file")


def get_data():
    return pd.read_excel(r'fake_data.xlsx', sheet_name="Sheet1", header=None)


def get_data_as_json():
    # Get formatted data as json
    data = get_data()
    json = [{
        "latitude": 0.0000,
        "longitude": 0.0000
    }]

    for row in data.iterrows():
        json.append({
            "latitude": float(row[1][0]),
            "longitude": float(row[1][1])
        })

    return json


connection = pymysql.connect(
    host=config.host,
    user=config.username,
    password=config.password,
    port=config.port,
    database=config.database
)


def upload_data():
    json = get_data_as_json()

    global connection
    connection.ping(reconnect=True)
    cursor = connection.cursor()
    query = "INSERT INTO locations (device_id, covid_status, latitude, longitude) VALUES (%s, %s, %s, %s)"
    device_id = 0
    for j in json:
        try:
            device_id = device_id - 1
            cursor.execute(
                query, (device_id, False, j["latitude"] * random.uniform(0.99, 1.01), j["longitude"] * random.uniform(0.99, 1.01)))
            connection.commit()
        except Exception as e:
            print("Update GPS failed, Error:", e)
            return False


upload_data()
