from flask import Flask, request, send_from_directory
from werkzeug.contrib.fixers import ProxyFix
import mysql.connector
import datetime
import json
import config

class mysqlManager:

    def __init__(self, server, username, passwd, db):
        self.my = mysql.connector.connect(user = username, password = passwd, host = server,
                                          database = db)
        self.cursor = self.my.cursor()

    def sqlinsert_from_json(self, data, table):
        fields = ''
        values = ''
        for k, v in data.items():
            fields = fields + '`' + k + '`, '
            values = values + str(v) + ', '
        fields = fields[:-2]
        values = values[:-2]
        datestr = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
        sql = 'INSERT INTO `%s` (`date`, %s) VALUES ("%s", %s);'%(table, fields, datestr, values)
        return sql

    def execute_sql(self, sql):
        try:
            self.cursor.execute(sql)
        except Exception as err:
            return str(err)
        else:
            try:
                rows = self.cursor.fetchall()
            except Exception:
                rows = []
            self.my.commit()
            return {'status':True, 'data': rows}

    def close(self):
        self.my.close()


app = Flask(__name__, static_url_path='')

@app.route('/')
def index():
    return app.send_static_file('./2.html')

@app.route('/stat')
def stat():
    return app.send_static_file('./stats.html')

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)

@app.route('/put', methods = ['POST'])
def put():
    data = request.json
    print data
    my = mysqlManager('127.0.0.1', config.mysql_username, config.mysql_password, config.mysql_database)
    datestr = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m')
    sql = my.sqlinsert_from_json(data, datestr)
    res = my.execute_sql(sql)
    my.close()
    if res['status'] is not True:
        response = app.response_class(
            response=(res),
            status=500,
            mimetype='text/html')
    else:
        response = app.response_class(
            status=200,
            mimetype='text/html')
    return response

@app.route('/sum')
def allsum():
    month = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m')
    my = mysqlManager('127.0.0.1', config.mysql_username, config.mysql_password, config.mysql_database)
    cols = ['food', 'transp', 'communal', 'health', 'bath', 'smoke',
            'cat', 'other', 'alco', 'etc']
    sums = {}
    for i in cols:
        sql = 'SELECT SUM(%s) FROM `%s`;'%(i, month)
        res = my.execute_sql(sql)
        if res['status'] is not True:
            response = app.response_class(
                response=(res),
                status=500,
                mimetype='text/html')
            return response
        else:
            sums[i] = res['data'][0][0]
    if sums != {}:
        datestr = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m')
        sql = 'SELECT * FROM `%s_money`;'%datestr
        res = my.execute_sql(sql)
        if res['status'] is not True:
            response = app.response_class(
                response=(res),
                status=500,
                mimetype='text/html')
        else:
            sums['mandatory'] = res['data'][0][1]
            sums['recreation'] = res['data'][0][2]
            sums['plan'] = res['data'][0][3]
            response = app.response_class(
                response=json.dumps(sums),
                status=200,
                mimetype='application/json')
    return response

@app.route('/report', methods = ['POST'])
def report():
    data = request.json
    month = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m')
    my = mysqlManager('127.0.0.1', config.mysql_username, config.mysql_password, config.mysql_database)
    sql = 'SELECT * FROM `%s` WHERE date BETWEEN "%s" AND "%s";'%(month, data['from'], data['to'])
    res = my.execute_sql(sql)
    cols = ['date', 'food', 'transp', 'communal', 'health', 'bath', 'smoke',
            'cat', 'other', 'alco', 'etc']
    result = []
    for i in res['data']:
        notnull = []
        for m in range(0,11):
            if i[m]!=0.0:
                notnull.append(m)
        rawjson = {}
        for n in notnull:
            if type(i[n]) is datetime.date:
                rawjson.update({cols[n]: datetime.datetime.strftime(i[n], '%Y-%m-%d')})
            else:
                rawjson.update({cols[n]: i[n]})
        result.append(rawjson)
        print rawjson
    print result
    if res['status'] is not True:
        response = app.response_class(
            response=(res),
            status=500,
            mimetype='text/html')
    else:
        response = app.response_class(
            response=json.dumps(result),
            status=200,
            mimetype='application/json')
    return response


app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == '__main__':
    #app.debug = True
    app.run('0.0.0.0')
