from json import dumps


from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify, send_from_directory, current_app
)
# from werkzeug.security import check_password_hash, generate_password_hash

from api.db import get_db, get_db_dicts


bp = Blueprint('graph', __name__, url_prefix='/graph')



@bp.route('/')
def graph():
    return render_template('graph/graph.html')