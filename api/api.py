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