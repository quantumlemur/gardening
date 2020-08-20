from json import dumps


from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify, send_from_directory, current_app
)
# from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db


bp = Blueprint('graph', __name__, url_prefix='/graph')



@bp.route('/')
def graph():
    db = get_db()
    error = None
    data = db.execute('SELECT timestamp, value FROM readings').fetchall()
    return render_template('graph/graph.html', data=data)