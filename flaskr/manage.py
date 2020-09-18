import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('manage', __name__, url_prefix='/manage')


@bp.route('/log', methods=('GET', 'POST'))
def view_log():
    db = get_db()
    error = None
    devices = db.execute('SELECT mac, name FROM devices').fetchall()
    print(len(devices))
    logs = {}
    for device in devices:
        print(device[0])
        logs[device[0]] = db.execute('SELECT log FROM device_status WHERE mac = ?', (device[0],)).fetchall()
    return render_template('manage/log.html', devices=devices, logs=logs)

