import functools
import hashlib

from datetime import datetime
from os import scandir


from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify, send_from_directory, current_app
)
# from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db


bp = Blueprint('api', __name__, url_prefix='/api')


def registration_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        db = get_db()
        if db.execute('SELECT mac FROM devices WHERE mac = ?', (request.headers['mac'],)).fetchone() is None:
            db.execute(
                'INSERT INTO devices (mac, username, password, name) VALUES (?, ?, ?, ?)',
                (request.headers['mac'], '0', '0', '')
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
def readings():
    db = get_db()
    error = None
    for reading in request.json:
        db.execute(
            'INSERT INTO readings (mac, timestamp, value, offset, name) VALUES (?, ?, ?, ?, ?)',
            (request.headers.get("mac"), reading[0], reading[1], reading[2], reading[3])
            )
        print("{} {} {} {}".format(datetime.fromtimestamp(reading[0]), reading[1], reading[2], reading[3]))
    db.commit()
    return "{\"status\": \"ok\"}"


@bp.route('/time')
def return_time():
    return { "time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f") }