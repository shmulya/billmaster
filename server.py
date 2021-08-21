from flask import Flask, request, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix
from modules.mysql_manager import mysqlManager
import modules.math_logic as process
import datetime
import json
import config


app = Flask(__name__, static_url_path='')
app.wsgi_app = ProxyFix(app.wsgi_app)


@app.route('/')
def index():
    return app.send_static_file('./add.html')


@app.route('/stat')
def stat():
    return app.send_static_file('./stats.html')


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)


@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)


@app.route('/put', methods=['POST'])
def put():
    data = request.json
    res = process.put(data)
    if res['status'] is not True:
        response = app.response_class(
            response=str(res),
            status=500,
            mimetype='text/html')
    else:
        response = app.response_class(
            status=200,
            mimetype='text/html')
    return response


@app.route('/sum')
def allsum():
    res = process.allsum()
    if res['status'] is not True:
        response = app.response_class(
            response=str(res),
            status=500,
            mimetype='text/html')
    else:
        response = app.response_class(
            response=json.dumps(res['data']),
            status=200,
            mimetype='application/json')
    return response


@app.route('/report', methods=['POST'])
def report():
    data = request.json
    res = process.report(data)
    if res['status'] is not True:
        response = app.response_class(
            response=str(res),
            status=500,
            mimetype='text/html')
    else:
        response = app.response_class(
            response=json.dumps(res['data']),
            status=200,
            mimetype='application/json')
    return response


if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0')
