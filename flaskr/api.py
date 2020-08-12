import functools
import hashlib

from os import scandir



from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify, send_from_directory, current_app
)
# from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db


bp = Blueprint('api', __name__, url_prefix='/api')


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