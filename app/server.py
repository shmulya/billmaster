from flask import Flask, request
from werkzeug.middleware.proxy_fix import ProxyFix
import modules.math_logic as process
import json


app = Flask(__name__, static_url_path='')
app.wsgi_app = ProxyFix(app.wsgi_app)


@app.route('/api/put', methods=['POST'])
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


@app.route('/api/sum')
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


@app.route('/api/report', methods=['POST'])
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
    app.run('0.0.0.0')
