from datetime import datetime, timezone, timedelta
import functools
import hashlib
from os import scandir
from re import compile, match, split
from statistics import mean, stdev
from time import time

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    jsonify,
    send_from_directory,
    current_app,
)
import pandas as pd

# from werkzeug.security import check_password_hash, generate_password_hash

from api.db import get_db, get_db_dicts


bp = Blueprint("api", __name__, url_prefix="/api")

calibration_time_window = 56  # days


@bp.route("/get_device_list", methods=("GET",))
def get_device_list():
    db = get_db_dicts()
    error = None
    devices = db.execute(
        """
        SELECT
            devices.*,
            name
        FROM
            devices
        LEFT JOIN device_config ON device_config.device_id = devices.id
        ORDER BY name
            """
    ).fetchall()
    return jsonify(devices)


@bp.route("/get_devices", methods=("GET",))
def get_devices():
    db = get_db_dicts()
    error = None
    devices = db.execute(
        """
        SELECT
            devices.*,
            device_config.*,
            device_status.*,
            mac,
            latest_soil_readings.value AS soil,
            latest_volt_readings.value AS volt,
            calibration.min,
            calibration.max,
            CAST(latest_soil_readings.value - calibration.min AS FLOAT) / (calibration.max - calibration.min) AS calibrated_value
        FROM
            devices
        LEFT JOIN (
            SELECT
                MAX(timestamp) AS timestamp,
                value,
                device_id
            FROM readings
            WHERE name="soil"
            AND zscore < 2
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
        LEFT JOIN (
            SELECT
                MAX(value) AS max,
                MIN(value) AS min,
                device_id
            FROM
                readings
            WHERE
                name = "soil" AND
                zscore < 2 AND
                timestamp > ?
            GROUP BY device_id
            ) AS calibration ON calibration.device_id = devices.id
        LEFT JOIN device_config ON device_config.device_id = devices.id
        LEFT JOIN device_status ON device_status.device_id = devices.id
        ORDER BY devices.id
            """,
        (int(time()) - calibration_time_window * 24 * 60 * 60,),
    ).fetchall()
    return jsonify(devices)


@bp.route("/get_device/<deviceId>", methods=("GET",))
def get_device(deviceId):
    assert deviceId == request.view_args["deviceId"]
    db = get_db_dicts()
    error = None
    devices = db.execute(
        """
        SELECT
            devices.*,
            device_config.*,
            device_status.*,
            mac,
            latest_soil_readings.value AS soil,
            latest_volt_readings.value AS volt,
            calibration.min,
            calibration.max,
            CAST(latest_soil_readings.value - calibration.min AS FLOAT) / (calibration.max - calibration.min) AS calibrated_value
        FROM
            devices
        LEFT JOIN (
            SELECT
                MAX(timestamp) AS timestamp,
                value,
                device_id
            FROM readings
            WHERE name="soil"
            AND zscore < 2
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
        LEFT JOIN (
            SELECT
                MAX(value) AS max,
                MIN(value) AS min,
                device_id
            FROM
                readings
            WHERE
                name = "soil" AND
                zscore < 2 AND
                timestamp > ?
            GROUP BY device_id
            ) AS calibration ON calibration.device_id = devices.id
        LEFT JOIN device_config ON device_config.device_id = devices.id
        LEFT JOIN device_status ON device_status.device_id = devices.id
        WHERE devices.id = ?
            """,
        (int(time()) - calibration_time_window * 24 * 60 * 60, deviceId),
    ).fetchone()
    return jsonify(devices)


@bp.route("/submit_config", methods=("POST",))
def submit_config():
    db = get_db()
    error = None

    db.execute(
        """
        UPDATE
            device_config
        SET
            name = ?,
            requested_version_tag = ?,
            board_type = ?,
            INIT_INTERVAL = ?,
            SLEEP_DURATION = ?,
            MAX_ENTRYS_WITHOUT_INIT = ?,
            LIGHT = ?,
            location_zone = ?,
            location_x = ?,
            location_y = ?
        WHERE device_id = ?""",
        (
            request.json["name"],
            request.json["requested_version_tag"],
            request.json["board_type"],
            request.json["INIT_INTERVAL"],
            request.json["SLEEP_DURATION"],
            request.json["MAX_ENTRYS_WITHOUT_INIT"],
            request.json["LIGHT"],
            request.json["location_zone"],
            request.json["location_x"],
            request.json["location_y"],
            request.json["id"],
        ),
    )
    db.commit()
    return request.json


@bp.route("/submit_location/<deviceId>", methods=("POST",))
def submit_location(deviceId):
    assert deviceId == request.view_args["deviceId"]
    db = get_db()
    error = None

    db.execute(
        """
        UPDATE
            device_config
        SET
            location_zone = ?,
            location_x = ?,
            location_y = ?
        WHERE device_id = ?""",
        (
            request.json["location_zone"],
            request.json["location_x"],
            request.json["location_y"],
            deviceId,
        ),
    )
    db.commit()
    return request.json


@bp.route("/get_all_sensor_data")
def get_all_sensor_data():
    db = get_db_dicts()
    error = None
    data = db.execute(
        """
        SELECT
            timestamp,
            value,
            readings.device_id,
            device_config.name
        FROM readings
        LEFT JOIN device_config
        ON readings.device_id = device_config.device_id
        WHERE
            readings.name = "soil" AND
            zscore < 2 AND
            timestamp > ?
        ORDER BY timestamp ASC
        """,
        (int(time()) - calibration_time_window * 24 * 60 * 60,),
    ).fetchall()
    return jsonify(data)


@bp.route("/get_sensor_data/<deviceId>/<sensorName>")
def get_sensor_data(deviceId, sensorName):
    assert deviceId == request.view_args["deviceId"]
    assert sensorName == request.view_args["sensorName"]
    db = get_db_dicts()
    error = None
    data = db.execute(
        """
        SELECT
            timestamp,
            value,
            device_id,
            name
        FROM readings
        WHERE
            device_id = ? AND
            name = ? AND
            zscore < 2 AND
            timestamp > ?
        ORDER BY timestamp ASC
        """,
        (
            deviceId,
            sensorName,
            int(time()) - calibration_time_window * 24 * 60 * 60,
        ),
    ).fetchall()
    if len(data) == 0:
        return jsonify([])

    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    df["value"] = pd.to_numeric(df["value"])
    df = df.set_index("timestamp")

    # exponential smoothing and resampling
    newdf = df.ewm(halflife="12 hours", times=df.index).mean()
    newdf = newdf.resample("1H").mean().bfill()

    newdf = newdf.reset_index()
    newdf.loc[:, "name"] = sensorName
    newdf.loc[:, "device_id"] = int(deviceId)
    newdf["timestamp"] = pd.to_numeric(newdf["timestamp"]) / 1000000000
    output = newdf.to_dict("records")
    # output = newdf
    # print(output)
    return jsonify(output)


@bp.route("/get_raw_sensor_data/<deviceId>/<sensorName>")
def get_raw_sensor_data(deviceId, sensorName):
    assert deviceId == request.view_args["deviceId"]
    assert sensorName == request.view_args["sensorName"]
    db = get_db_dicts()
    error = None
    data = db.execute(
        """
        SELECT
            timestamp,
            value,
            device_id,
            name
        FROM readings
        WHERE
            device_id = ? AND
            name = ? AND
            timestamp > ?
        ORDER BY timestamp ASC
        """,
        (
            deviceId,
            sensorName,
            int(time()) - calibration_time_window * 24 * 60 * 60,
        ),
    ).fetchall()
    return jsonify(data)


@bp.route("/get_zones")
def get_zones():
    db = get_db_dicts()
    error = None
    data = db.execute(
        """
        SELECT
           *
        FROM zones
        """
    ).fetchall()
    return jsonify(data)


@bp.route("/get_firmware_versions", methods=("GET",))
def get_firmware_versions():
    pattern = compile("((\d+[\.\-])+)")
    file_list = []
    with scandir("firmware/versions") as files:
        for f in files:
            if f.is_file() and f.name[-4:] == ".bin":
                strippedVersion = pattern.search(f.name)
                if strippedVersion:
                    splitVersion = split("\.|\-", strippedVersion.group(0).strip("-."))
                    parsed_version = [int(s) for s in splitVersion]

                    file_list.append(
                        {
                            "tag": f.name[:-4],
                            "parsed_version": parsed_version,
                        }
                    )
    file_list = sorted(file_list, key=lambda x: x["parsed_version"], reverse=True)
    file_list = [{"label": item["tag"], "value": item["tag"]} for item in file_list]
    return jsonify(file_list)


@bp.route("/get_board_types", methods=("GET",))
def get_board_types():
    file_list = []
    db = get_db_dicts()
    data = db.execute(
        """
        SELECT
            board_name AS label,
            board_type AS value
        FROM
            board_types"""
    ).fetchall()
    # output = [
    #     {"label": item["board_name"], "value": item["board_type"]} for item in data
    # ]
    return jsonify(data)


@bp.route("/do_watering/<deviceId>")
def do_watering(deviceId):
    assert deviceId == request.view_args["deviceId"]
    db = get_db_dicts()
    error = None
    db.execute(
        """
        INSERT INTO readings
            (
                timestamp,
                value,
                device_id,
                name,
                offset,
                zscore
            )
        VALUES
            (
                ?,
                1,
                ?,
                "watering",
                0,
                0
            )
        """,
        (int(time()), deviceId),
    )
    db.commit()
    return {"success": True}


@bp.route("/time")
def return_time():
    return {"time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")}
