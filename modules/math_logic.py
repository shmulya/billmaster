from modules.mysql_manager import mysqlManager
import datetime
import config


def put(data):
    my = mysqlManager('127.0.0.1', config.mysql_username, config.mysql_password, config.mysql_database)
    datestr = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m')
    sql = my.sqlinsert_from_json(data, datestr)
    res = my.execute_sql(sql)
    my.close()
    return res


def allsum():
    month = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m')
    my = mysqlManager('127.0.0.1', config.mysql_username, config.mysql_password, config.mysql_database)
    cols = ['food', 'transp', 'communal', 'health', 'bath', 'smoke',
            'cat', 'other', 'alco', 'etc']
    sums = {}
    for i in cols:
        sql = f'SELECT SUM({i}) FROM `{month}`;'
        res = my.execute_sql(sql)
        if res['status'] is not True:
            my.close()
            return res
        else:
            sums[i] = float(str(res['data'][0][0]))
    if sums != {}:
        sql = f'SELECT * FROM `{month}_money`;'
        res = my.execute_sql(sql)
        if res['status'] is not True:
            return res
        else:
            sums['mandatory'] = res['data'][0][0]
            sums['recreation'] = res['data'][0][1]
            sums['plan'] = res['data'][0][2]
            return {'status': True, 'data': sums}


def report(data):
    month = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m')
    my = mysqlManager('127.0.0.1', config.mysql_username, config.mysql_password, config.mysql_database)
    sql = f'SELECT * FROM `{month}` WHERE date BETWEEN "{data["from"]}" AND "{data["to"]}";'
    res = my.execute_sql(sql)
    my.close()
    cols = ['date', 'food', 'transp', 'communal', 'health', 'bath', 'smoke',
            'cat', 'other', 'alco', 'etc']
    result = []
    for i in res['data']:
        print(i)
        notnull = []
        for m in range(0, len(cols)):
            if i[m] != 0:
                notnull.append(m)
        rawjson = {}
        for n in notnull:
            if type(i[n]) is datetime.date:
                rawjson.update({cols[n]: datetime.datetime.strftime(i[n], '%Y-%m-%d')})
            else:
                rawjson.update({cols[n]: float(str(i[n]))})
        result.append(rawjson)
    if res['status'] is not True:
        return res
    else:
        return {'status': True, 'data': result}
