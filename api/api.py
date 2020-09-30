import functools
import hashlib

from datetime import datetime, timezone, timedelta
from os import scandir


from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify, send_from_directory, current_app
)
# from werkzeug.security import check_password_hash, generate_password_hash

from api.db import get_db, get_db_dicts


bp = Blueprint('api', __name__, url_prefix='/api')


def registration_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        db = get_db()
        device_id = db.execute('SELECT id FROM devices WHERE mac = ?', (request.headers['mac'],)).fetchone()
        if device_id is None:
            db.execute(
                'INSERT INTO devices (mac) VALUES (?)',
                (request.headers['mac'],)
                )
            device_id = db.execute('SELECT id FROM devices WHERE mac = ?', (request.headers['mac'],)).fetchone()
            db.execute(
                """INSERT INTO device_config
                    (device_id,
                    name)
                    VALUES (?, ?)""",
                (device_id[0], request.headers['mac'])
                )
            db.execute(
                """INSERT INTO device_status
                    (device_id
                    )
                    VALUES (?)""",
                (device_id[0],)
                )
            db.commit()
        return view(**kwargs)

    return wrapped_view


def update_checkin(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        db = get_db()
        device_id = db.execute('SELECT id FROM devices WHERE mac = ?', (request.headers['mac'],)).fetchone()
        print(device_id[0], datetime.now())
        if device_id is not None:
            db.execute(
                """UPDATE device_status
                SET checkin_time = ?
                WHERE
                device_id = ?""",
                (datetime.now(), device_id[0],)
                )
            db.commit()
        return view(**kwargs)

    return wrapped_view


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


@bp.route('/listfiles', methods=('GET', 'POST'))
def listfiles():
    file_list = []
    with scandir('nodemcu/exposed') as files:
        for f in files:
            if f.is_file():
                file_list.append([f.name, md5('nodemcu/exposed/' + f.name)])
    return jsonify(file_list)


@bp.route('/getfile/<path:filename>', methods=('GET', 'POST'))
def getfile(filename):
    return send_from_directory(current_app.config['NODEMCU_FILE_PATH'], filename)


@bp.route('/status', methods=('GET', 'POST'))
def status():
    db = get_db()
    error = None
    db.execute(
        'INSERT INTO device_status (voltage) VALUES (?)',
        (request.json.voltage,)
        )
    print("{}".format(request.json.voltage))
    db.commit()
    return "{\"status\": \"ok\"}"


@bp.route('/log', methods=('GET', 'POST'))
@registration_required
@update_checkin
def store_log():
    db = get_db()
    error = None
    db.execute(
        'INSERT INTO device_status (mac, log) VALUES (?, ?)',
        (request.headers.get("mac"), request.data)
        )
    db.commit()
    return "{\"status\": \"ok\"}"


@bp.route('/readings', methods=('GET', 'POST'))
@registration_required
@update_checkin
def readings():
    db = get_db()
    error = None
    device_id = db.execute('SELECT id FROM devices WHERE mac = ?', (request.headers['mac'],)).fetchone()
    if device_id is not None:
        for reading in request.json:
            db.execute(
                """INSERT INTO readings
                (
                    device_id,
                    timestamp,
                    value,
                    offset,
                    name
                )
                VALUES (?, ?, ?, ?, ?)""",
                (
                    device_id[0],
                    datetime.fromtimestamp(reading[0]),
                    reading[1],
                    reading[2],
                    reading[3]
                )
            )
            print("{} {} {} {}".format(datetime.fromtimestamp(reading[0]), reading[1], reading[2], reading[3]))
        db.commit()



        # recalibrate sensors
        calibration_time_window = 7 # days
        db.execute("""
            UPDATE
                device_config
            SET
                calibration_max = (
                    SELECT
                        MAX(value)
                    FROM
                        readings
                    WHERE
                        name = "soil" AND
                        device_id = ? AND
                        timestamp > ?
                    )
            WHERE
                device_id = ?
            """,
            (
                device_id[0],
                datetime.now(timezone.utc) - timedelta(days=calibration_time_window),
                device_id[0]
            ))
        db.execute("""
            UPDATE
                device_config
            SET
                calibration_min = (
                    SELECT
                        MIN(value)
                    FROM
                        readings
                    WHERE
                        name = "soil" AND
                        device_id = ? AND
                        timestamp > ?
                    )
            WHERE
                device_id = ?
            """,
            (
                device_id[0],
                datetime.now(timezone.utc) - timedelta(days=calibration_time_window),
                device_id[0]
            ))
        db.commit()



    return "{\"status\": \"ok\"}"


@bp.route('/config', methods=('GET',))
@registration_required
@update_checkin
def config():
    db = get_db()
    error = None
    config = db.execute(
        """SELECT
            mac,
            INIT_INTERVAL,
            SLEEP_DURATION,
            SLEEP_DELAY,
            LIGHT
            from device_config
            JOIN devices ON devices.id = device_config.device_id
            WHERE mac = ?""",
        (request.headers.get("mac"),)
        ).fetchone()
    json = {
        'mac': config[0],
        'INIT_INTERVAL': config[1],
        'SLEEP_DURATION': config[2],
        'SLEEP_DELAY': config[3],
        'LIGHT': config[4]
        }
    return json


@bp.route('/submit_config', methods=('POST',))
def submit_config():
    db = get_db()
    error = None

    db.execute(
        """UPDATE device_config
            SET
            name = ?,
            INIT_INTERVAL = ?,
            SLEEP_DURATION = ?,
            SLEEP_DELAY = ?,
            LIGHT = ?,
            calibration_min = ?,
            calibration_max = ?,
            trigger_min = ?
            WHERE device_id = ?""",
        (
            request.form['name'],
            request.form['INIT_INTERVAL'],
            request.form['SLEEP_DURATION'],
            request.form['SLEEP_DELAY'],
            request.form['LIGHT'],
            request.form['calibration_min'],
            request.form['calibration_max'],
            request.form['trigger_min'],
            request.form['id']
        ))
    db.commit()
    return request.form


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
        WHERE readings.name = "soil"
        """).fetchall()
    return jsonify(data)


@bp.route('/time')
def return_time():
    return { "time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f") }