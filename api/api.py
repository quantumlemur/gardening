import functools
import hashlib

from datetime import datetime, timezone, timedelta
from statistics import mean, stdev
from time import time
from os import scandir


from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify, send_from_directory, current_app
)
# from werkzeug.security import check_password_hash, generate_password_hash

from api.db import get_db, get_db_dicts


bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/get_devices', methods=('GET',))
def get_devices():
    db = get_db_dicts()
    error = None
    devices = db.execute("""
        SELECT
            devices.id,
            mac,
            device_config.name,
            checkin_time,
            device_next_init,
            location_zone,
            location_x,
            location_y,
            INIT_INTERVAL,
            SLEEP_DURATION,
            MAX_ENTRYS_WITHOUT_INIT,
            LIGHT,
            calibration_min,
            calibration_max,
            trigger_min,
            timestamp,
            latest_soil_readings.value AS soil,
            latest_volt_readings.value AS volt,
            CAST(latest_soil_readings.value - calibration_min AS FLOAT) / (calibration_max - calibration_min) AS calibrated_value
        FROM
            devices
        LEFT JOIN (
            SELECT
                MAX(timestamp) AS timestamp,
                value,
                device_id
            FROM readings
            WHERE name="soil"
            GROUP BY device_id
            ) AS latest_soil_readings ON latest_soil_readings.device_id = devices.id
        LEFT JOIN (
            SELECT
                MAX(timestamp),
                value,
                device_id
            FROM readings
            WHERE name="volt"
            GROUP BY device_id
            ) AS latest_volt_readings ON latest_volt_readings.device_id = devices.id
        LEFT JOIN device_config ON device_config.device_id = devices.id
        LEFT JOIN device_status ON device_status.device_id = devices.id
            """).fetchall()
    return jsonify(devices)


@bp.route('/submit_config', methods=('POST',))
def submit_config():
    db = get_db()
    error = None

    db.execute("""
        UPDATE
            device_config
        SET
            name = ?,
            INIT_INTERVAL = ?,
            SLEEP_DURATION = ?,
            MAX_ENTRYS_WITHOUT_INIT = ?,
            LIGHT = ?,
            calibration_min = ?,
            calibration_max = ?,
            trigger_min = ?,
            location_zone = ?,
            location_x = ?,
            location_y = ?
        WHERE device_id = ?""",
               (
                   request.json['name'],
                   request.json['INIT_INTERVAL'],
                   request.json['SLEEP_DURATION'],
                   request.json['MAX_ENTRYS_WITHOUT_INIT'],
                   request.json['LIGHT'],
                   request.json['calibration_min'],
                   request.json['calibration_max'],
                   request.json['trigger_min'],
                   request.json['location_zone'],
                   request.json['location_x'],
                   request.json['location_y'],
                   request.json['id']
               ))
    db.commit()
    return request.json


@bp.route('/get_sensor_data')
def get_sensor_data():
    db = get_db_dicts()
    error = None
    data = db.execute("""
        SELECT
            timestamp,
            value,
            CAST(value - calibration_min AS FLOAT) / (calibration_max - calibration_min) AS calibrated_value,
            readings.device_id,
            device_config.name
        FROM readings
        LEFT JOIN device_config
        ON readings.device_id = device_config.device_id
        WHERE
            readings.name = "soil" AND
            zscore < 2 AND
            timestamp > ?
        """,
                      (
                          int(time()) - 14 * 24 * 60 * 60,
                      )).fetchall()
    return jsonify(data)


@bp.route('/get_raw_sensor_data/<path:deviceid>')
def get_raw_sensor_data(deviceid):
    db = get_db_dicts()
    error = None
    data = db.execute("""
        SELECT
            timestamp,
            value,
            zscore,
            readings.device_id,
            device_config.name,
            readings.name AS sensor
        FROM readings
        LEFT JOIN device_config
        ON readings.device_id = device_config.device_id
        WHERE
            timestamp > ? AND
            readings.device_id = ?
        """,
                      (
                          int(time()) - 14 * 24 * 60 * 60,
                          deviceid
                      )).fetchall()
    return jsonify(data)


@bp.route('/time')
def return_time():
    return {"time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")}
