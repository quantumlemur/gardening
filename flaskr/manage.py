import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db_dicts

bp = Blueprint('manage', __name__, url_prefix='/manage')


@bp.route('/', methods=('GET',))
def manage_devices():
    db = get_db_dicts()
    error = None
    devices = db.execute(
            """SELECT
                devices.id,
                mac,
                device_config.name,
                checkin_time,
                INIT_INTERVAL,
                SLEEP_DURATION,
                SLEEP_DELAY,
                LIGHT,
                calibration_min,
                calibration_max,
                trigger_min,
                timestamp,
                value
                FROM (
                    SELECT
                    MAX(timestamp) AS latest_timestamp,
                    device_id
                    FROM readings
                    WHERE name = "soil"
                    GROUP BY device_id
                ) AS latest_reading_timestamps
                JOIN device_config ON device_config.device_id = latest_reading_timestamps.device_id
                JOIN devices ON devices.id = device_config.device_id
                LEFT JOIN device_status ON devices.id = device_status.device_id
                LEFT JOIN readings ON
                    readings.device_id = latest_reading_timestamps.device_id AND
                    readings.timestamp = latest_reading_timestamps.latest_timestamp
            """).fetchall()
    return render_template('manage/manage.html', devices=devices)


@bp.route('/log', methods=('GET',))
def view_log():
    db = get_db()
    error = None
    devices = db.execute('SELECT mac, name FROM devices').fetchall()
    logs = {}
    for device in devices:
        logs[device[0]] = db.execute('SELECT log FROM device_status WHERE mac = ?', (device[0],)).fetchall()
    return render_template('manage/log.html', devices=devices, logs=logs)

