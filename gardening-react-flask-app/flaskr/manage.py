import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('manage', __name__, url_prefix='/manage')


@bp.route('/manage', methods=('GET',))
def manage_devices():
    db = get_db()
    error = None
    devices = db.execute(
            """SELECT
                mac,
                name,
                checkin_time,
                INIT_INTERVAL,
                SLEEP_DURATION,
                SLEEP_DELAY,
                LIGHT
                FROM device_config
                JOIN devices ON devices.id = device_config.device_id
                LEFT JOIN device_status ON devices.id = device_status.device_id"""
            ).fetchall()
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

