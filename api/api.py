import functools
import hashlib

from datetime import datetime, timezone, timedelta
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
	return jsonify(devices)


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
			request.json['name'],
			request.json['INIT_INTERVAL'],
			request.json['SLEEP_DURATION'],
			request.json['SLEEP_DELAY'],
			request.json['LIGHT'],
			request.json['calibration_min'],
			request.json['calibration_max'],
			request.json['trigger_min'],
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
			timestamp > ?
		""", 
		(
			int(time()) - 14 * 24 * 60 * 60,
		)).fetchall()
	return jsonify(data)


@bp.route('/time')
def return_time():
	return { "time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f") }