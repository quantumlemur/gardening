from flask import Flask, request, send_from_directory
from os import scandir


import hashlib
import json


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


app = Flask(__name__, static_url_path='')


@app.route('/')
def hello_world():
    data = request.args['data']
    print(data)
    return 'Hello, World!'


@app.route('/files/<path:path>')
def send_file(path):
    return send_from_directory('nodemcu/exposed', path)


@app.route('/listfiles')
def list_files():
    file_list = []
    with scandir('nodemcu/exposed') as files:
        for f in files:
            if f.is_file():
                file_list.append([f.name, md5('nodemcu/exposed/' + f.name)])
    return json.dumps(file_list)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
