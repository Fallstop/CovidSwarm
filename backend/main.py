#!/usr/bin/python3
from flask import Flask, request, jsonify
from flask.json import JSONEncoder
from datetime import date
import json
import pymysql

try:
    import config
except Exception:
    print("Please make config.py file and copy contents from dev info file")


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, date):
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)


app = Flask("CoVID-SWARM")
app.json_encoder = CustomJSONEncoder

# Connection info for database
connection = pymysql.connect(
    host=config.host,
    user=config.username,
    password=config.password,
    port=config.port,
    database=config.database
)


@app.route("/location/<int:device_id>", methods=['POST'])
def update_location(device_id: int):
    # For JSON Payload
    payload = request.get_json(force=True)
    if payload is None:
        return '', 204

    latitude = payload["latitude"]
    longitude = payload["longitude"]
    covid_status = payload["covid_status"]

    if not update_GPS(device_id, covid_status, latitude, longitude):
        return '', 500

    # Update location
    # return "Longitude: {}, Latitude: {}, Covid: {}".format(longitude, latitude, covid_status), 200
    return '', 200


@app.route("/location", methods=['GET'])
def get_location():
    # Get values from database
    payload = get_GPS()

    # Get last location
    return jsonify(payload), 200


@app.route("/device", methods=["GET"])
def device():
    device = reg_device()
    if not False:
        print("Device:", device)
        return str(device), 200

    return '', 500


@app.route("/covid", methods=["GET"])
def covid_cases():
    payload = get_active_cases()
    if not False:   
        return jsonify(payload), 200
    return '',500

@app.route("/app/version", methods=["GET"])
def app_version():
    payload = get_latest_app_version()
    if not False:
        return jsonify(payload), 200
    return '', 500


def reg_device():
    global connection
    connection.ping(reconnect=True)
    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO device_registration VALUES ();")
        connection.commit()
        cursor.execute("SELECT LAST_INSERT_ID();")
        return cursor.fetchone()[0]
    except Exception as e:
        print("Device Registration failed, Error:", e)
        return False


def update_GPS(device_id, covid_status, latitude, longitude):
    global connection
    connection.ping(reconnect=True)
    cursor = connection.cursor()
    query = "INSERT INTO locations (device_id, covid_status, latitude, longitude) VALUES (%s, %s, %s, %s)"
    try:
        cursor.execute(query, (device_id, covid_status, latitude, longitude))
        connection.commit()
        return True
    except Exception as e:
        print("Update GPS failed, Error:", e)
        return False


def get_GPS():
    global connection
    connection.ping(reconnect=True)
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
    query = "select covid_status, latitude, longitude, max(time_gps) as latest_time from locations group by device_id"

    try:
        cursor.execute(query)
        result = cursor.fetchall()
        print("Result: ", result)
        return result
    except Exception as e:
        print("Get GPS failed, Error:", e)
        return False


def get_active_cases():
    global connection
    connection.ping(reconnect=True)
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
    query = "SELECT * FROM covid_cases"

    try:
        cursor.execute(query)
        result = cursor.fetchall()
        print("Active cases result: ", result)
        return result
    except Exception as e:
        print("Get CoVID Failed, Error:", e)
        return False

def get_latest_app_version():
    global connection
    connection.ping(reconnect=True)
    cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)
    query = "SELECT * FROM app_version"

    try:
        cursor.execute(query)
        result = cursor.fetchall()
        print("App version result: ", result[0])
        return result[0]
    except Exception as e:
        print("Getting covid cases failed, Error:", e)
        return False


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
