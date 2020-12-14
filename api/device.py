import functools
from hashlib import md5, sha256
from re import compile, match, split
from statistics import mean, stdev
from time import time
from os import path, scandir

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

# from werkzeug.security import check_password_hash, generate_password_hash

from api.db import get_db, get_db_dicts


bp = Blueprint("device", __name__, url_prefix="/device")

calibration_time_window = 28  # days


def registration_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        db = get_db()
        if "mac" not in request.headers:
            error = "no mac in headers"
            flash(error)
        else:
            device_id = db.execute(
                "SELECT id FROM devices WHERE mac = ?", (request.headers["mac"],)
            ).fetchone()
            if device_id is None:
                db.execute(
                    "INSERT INTO devices (mac, created) VALUES (?, ?)",
                    (request.headers["mac"], int(time())),
                )
                device_id = db.execute(
                    "SELECT id FROM devices WHERE mac = ?", (request.headers["mac"],)
                ).fetchone()
                db.execute(
                    """INSERT INTO device_config
                        (device_id,
                        name,
                        board_type)
                        VALUES (?, ?, 2)""",
                    (device_id[0], request.headers["mac"]),
                )
                db.execute(
                    """INSERT INTO device_status
                        (device_id
                        )
                        VALUES (?)""",
                    (device_id[0],),
                )
                # Insert alternating points, a few weeks into the past. This will
                # give a semi-appropriate scale until more data has been collected.
                # Timestamp the data such that 7 days elapse before it passes out
                # of the calibration time window.
                for i in range(10):
                    db.execute(
                        """
                        INSERT INTO readings
                        (
                            device_id,
                            timestamp,
                            value,
                            offset,
                            name,
                            zscore
                        )
                        VALUES(?, ?, ?, ?, ?, ?)""",
                        (
                            device_id[0],
                            int(time()) - (calibration_time_window - 7) * 60 * 60 * 24,
                            350,
                            0,
                            "soil",
                            1,
                        ),
                    )
                    db.execute(
                        """
                        INSERT INTO readings
                        (
                            device_id,
                            timestamp,
                            value,
                            offset,
                            name,
                            zscore
                        )
                        VALUES(?, ?, ?, ?, ?, ?)""",
                        (
                            device_id[0],
                            int(time())
                            - (calibration_time_window - 7) * 60 * 60 * 24
                            + 1,
                            650,
                            0,
                            "soil",
                            1,
                        ),
                    )
                db.commit()
        return view(**kwargs)

    return wrapped_view


def update_checkin(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        db = get_db()
        mac = request.headers["mac"]
        device_id = db.execute(
            "SELECT id FROM devices WHERE mac = ?", (mac,)
        ).fetchone()
        if device_id is not None:
            device_id = device_id[0]
            # Update check-in time
            db.execute(
                """UPDATE device_status
				SET
					checkin_time = ?
				WHERE
					device_id = ?""",
                (int(time()), device_id),
            )
            # Iterate through the other optional parameters
            optional_params = [
                "current_version_hash",
                "current_version_tag",
                "device_next_init",
                "device_time",
            ]
            for param in optional_params:
                if param in request.headers:
                    db.execute(
                        """UPDATE device_status
                        SET
                            {} = ?
                        WHERE
                            device_id = ?""".format(
                            param
                        ),
                        (request.headers[param], device_id),
                    )
            db.commit()
        return view(**kwargs)

    return wrapped_view


def md5_file(fname):
    hash_md5 = md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def sha256_file(fname):
    hash_sha256 = sha256()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


@bp.route("/listfiles", methods=("GET", "POST"))
def listfiles():
    file_list = []
    with scandir("nodemcu/public") as files:
        for f in files:
            if f.is_file() and (f.name[-4:] == ".lua" or f.name[-4:] == ".cfg"):
                file_list.append([f.name, md5_file("nodemcu/public/" + f.name)])
    return jsonify(file_list)


@bp.route("/getfile/<path:filename>", methods=("GET", "POST"))
def getfile(filename):
    return send_from_directory(current_app.config["NODEMCU_FILE_PATH"], filename)


@bp.route("/getfile_python/<path:filename>", methods=("GET", "POST"))
def getfile_python(filename):
    return send_from_directory(current_app.config["MICROPYTHON_FILE_PATH"], filename)


@bp.route("/listfiles_python", methods=("GET", "POST"))
def listfiles_python():
    file_list = []
    with scandir("micropython/src") as files:
        for f in files:
            if f.is_file() and (f.name[-3:] == ".py" or f.name[-4:] == ".cfg"):
                file_list.append([f.name, sha256_file("micropython/src/" + f.name)])
    return jsonify(file_list)


@bp.route("/getfile_python_v2/<path:filename>", methods=("GET", "POST"))
def getfile_python_v2(filename):
    return send_from_directory("../firmware/main", filename)


@bp.route("/listfiles_python_v2", methods=("GET", "POST"))
def listfiles_python_v2():
    file_list = []
    with scandir("firmware/main") as files:
        for f in files:
            if f.is_file() and (f.name[-3:] == ".py" or f.name[-4:] == ".cfg"):
                file_list.append([f.name, sha256_file("firmware/main/" + f.name)])
    return jsonify(file_list)


@bp.route("/list_versions", methods=("GET",))
def list_versions():
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
                            "filename": f.name,
                            "sha256": sha256_file(
                                "firmware/versions/{}".format(f.name)
                            ),
                            "size": path.getsize("firmware/versions/{}".format(f.name)),
                            "parsed_version": parsed_version,
                        }
                    )
    return jsonify(sorted(file_list, key=lambda x: x["parsed_version"], reverse=True))


@bp.route("/get_firmware/<path:filename>", methods=("GET", "POST"))
@registration_required
@update_checkin
def get_firmware(filename):
    print(request.headers["mac"])
    print(request.headers)
    if "mac" in request.headers:
        db = get_db()
        device_id = db.execute(
            "SELECT id FROM devices WHERE mac = ?", (request.headers["mac"],)
        ).fetchone()
        if device_id:
            device_id = device_id[0]
            db.execute(
                """
                UPDATE
                    device_status
                SET
                    last_update_attempt_time=?,
                    last_update_attempt_tag=?
                WHERE
                    device_id=?""",
                (int(time()), filename[:-4], device_id),
            )
            db.commit()
    return send_from_directory("../firmware/versions", filename)


@bp.route("/status", methods=("GET", "POST"))
def status():
    db = get_db()
    error = None
    db.execute(
        "INSERT INTO device_status (voltage) VALUES (?)", (request.json.voltage,)
    )
    db.commit()
    return '{"status": "ok"}'


@bp.route("/log", methods=("GET", "POST"))
@registration_required
@update_checkin
def store_log():
    db = get_db()
    error = None
    db.execute(
        "INSERT INTO device_status (mac, log) VALUES (?, ?)",
        (request.headers.get("mac"), request.data),
    )
    db.commit()
    return '{"status": "ok"}'


@bp.route("/readings", methods=("GET", "POST"))
@registration_required
@update_checkin
def readings():
    db = get_db()
    error = None
    device_id = db.execute(
        "SELECT id FROM devices WHERE mac = ?", (request.headers["mac"],)
    ).fetchone()[0]
    calibrationTimeMin = int(time()) - calibration_time_window * 24 * 60 * 60
    pastReadings = {}  # Cached values of past readings

    for reading in request.json:
        timestamp, value, offset, sensorName = reading
        # select data from last time period and calculate mean and stddev
        if sensorName not in pastReadings:
            data = db.execute(
                """
                SELECT
                    value
                FROM
                    readings
                WHERE
                    device_id = ? AND
                    readings.name = ? AND
                    timestamp > ?
                """,
                (device_id, sensorName, calibrationTimeMin),
            ).fetchall()
            pastReadings[sensorName] = [row[0] for row in data]

        pastReadings[sensorName].append(value)
        avg = mean(pastReadings[sensorName])
        stddev = 1
        if len(pastReadings[sensorName]) > 1:
            stddev = stdev(pastReadings[sensorName])

        # insert value into table
        zscore = abs(value - avg) / stddev
        db.execute(
            """INSERT INTO readings
            (
                device_id,
                timestamp,
                value,
                offset,
                name,
                zscore
            )
            VALUES (?, ?, ?, ?, ?, ?)""",
            (device_id, timestamp, value, offset, sensorName, zscore),
        )

        # # recalibrate sensors
        # db.execute(
        #     """
        #     UPDATE
        #         device_config
        #     SET
        #         calibration_max = (
        #             SELECT
        #                 MAX(value)
        #             FROM
        #                 readings
        #             WHERE
        #                 name = "soil" AND
        #                 zscore < 2 AND
        #                 device_id = ? AND
        #                 timestamp > ?
        #             ),
        #         calibration_min = (
        #             SELECT
        #                 MIN(value)
        #             FROM
        #                 readings
        #             WHERE
        #                 name = "soil" AND
        #                 zscore < 2 AND
        #                 device_id = ? AND
        #                 timestamp > ?
        #             )
        #     WHERE
        #         device_id = ?
        #     """,
        #     (
        #         device_id,
        #         int(time()) - calibration_time_window * 24 * 60 * 60,
        #         device_id,
        #         int(time()) - calibration_time_window * 24 * 60 * 60,
        #         device_id,
        #     ),
        # )

    db.commit()
    return '{"status": "ok"}'


@bp.route("/config", methods=("GET",))
@registration_required
@update_checkin
def config():
    db = get_db_dicts()
    error = None
    deviceConfig = db.execute(
        """
        SELECT
			*
        FROM device_config
        JOIN devices ON devices.id = device_config.device_id
        LEFT JOIN board_types ON device_config.board_type = board_types.board_type
        WHERE mac = ?
        """,
        (request.headers.get("mac"),),
    ).fetchone()
    return jsonify(deviceConfig)
