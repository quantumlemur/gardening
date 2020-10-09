from json import dumps


from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify, send_from_directory, current_app
)
# from werkzeug.security import check_password_hash, generate_password_hash

from api.db import get_db, get_db_dicts


bp = Blueprint('map', __name__, url_prefix='/map')


@bp.route('/')
def map():
    db = get_db()
    error = None
    devices = db.execute("""
        SELECT
            device_id,
            name,
            location_y,
            location_y
        FROM
            device_config
        """)
    return render_template('map/map.html', devices=devices)
