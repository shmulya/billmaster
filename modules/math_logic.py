from modules.mysql_manager import mysqlManager
import datetime
import config
import schedule
import time


def put(data):
    my = mysqlManager('127.0.0.1', config.mysql_username, config.mysql_password, config.mysql_database)
    datestr = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m')
    sql = my.sqlinsert_from_json(data, datestr)
    res = my.execute_sql(sql)
    my.close()
    return res


def allsum():
    month = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m')
    today = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
    my = mysqlManager('127.0.0.1', config.mysql_username, config.mysql_password, config.mysql_database)
    cols = ['food', 'transp', 'health', 'home',
            'smoke', 'cat', 'other', 'alco', 'etc']
    sums = {}
    # подсчёт трат за месяц по категориям
    for i in cols:
        sql = f'SELECT SUM({i}) FROM `{month}`;'
        res = my.execute_sql(sql)
        if res['status'] is not True:
            my.close()
            return res
        else:
            sums[i] = float(str(res['data'][0][0]))
    # подсчёт трат за день
    per_day = 0
    for i in cols:
        sql = f'SELECT SUM({i}) FROM `{month}` WHERE date="{today}";'
        res = my.execute_sql(sql)
        if res['status'] is not True:
            my.close()
            return res
        else:
            try:
                per_day = per_day + float(str(res['data'][0][0]))
            except Exception:
                per_day = 0
    all = 0
    for v in sums.values():
        all = all + v
    sums['all'] = all
    # подсчёт баланса
    if sums != {}:
        sql = f'SELECT * FROM `{month}_money`;'
        res = my.execute_sql(sql)
        if res['status'] is not True:
            my.close()
            return res
        else:
            sums['available'] = float(str(res['data'][0][0]))
            sums['mandatory'] = float(str(res['data'][0][1]))
            sums['spending'] = sums['available'] - sums['mandatory']
            sums['per_day'] = round(sums['spending'] / 30, 2)
            sums['balance'] = sums['spending'] - sums['all']
            sums['spending_today'] = per_day
            sums['remain_today'] = round(sums['per_day'] - sums['spending_today'], 2)
            # Получение баланса из копилки
            sql = f'SELECT balance FROM `{month}_money_box`;'
            res = my.execute_sql(sql)
            if res['status'] is not True:
                sums['money_box'] = None
            else:
                sums['money_box'] = float(str(res['data'][0][0]))
            my.close()
            return {'status': True, 'data': sums}


def report(data):
    month = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m')
    my = mysqlManager('127.0.0.1', config.mysql_username, config.mysql_password, config.mysql_database)
    sql = f'SELECT * FROM `{month}` WHERE date BETWEEN "{data["from"]}" AND "{data["to"]}";'
    res = my.execute_sql(sql)
    my.close()
    cols = ['date', 'food', 'transp', 'health', 'home',
            'smoke', 'cat', 'other', 'alco', 'etc']
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


def money_box_counter():
    month = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m')
    today = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
    my = mysqlManager('127.0.0.1', config.mysql_username, config.mysql_password, config.mysql_database)
    cols = ['food', 'transp', 'health', 'home',
            'smoke', 'cat', 'other', 'alco', 'etc']
    # подсчёт трат за день
    today = 0
    for i in cols:
        sql = f'SELECT SUM({i}) FROM `{month}` WHERE date="{today}";'
        res = my.execute_sql(sql)
        if res['status'] is not True:
            my.close()
            return res
        else:
            try:
                today = today + float(str(res['data'][0][0]))
            except:
                today = 0
    sql = f'SELECT * FROM `{month}_money`;'
    res = my.execute_sql(sql)
    if res['status'] is not True:
        my.close()
        return res
    else:
        available = float(str(res['data'][0][0]))
        mandatory = float(str(res['data'][0][1]))
        spending = available - mandatory
        per_day = round(spending / 30, 2)
        # Получение баланса из копилки
        sql = f'SELECT balance FROM `{month}_money_box`;'
        res = my.execute_sql(sql)
        if res['status'] is not True:
            money_box = None
        else:
            money_box = float(str(res['data'][0][0]))
        # новый баланс копилки
        money_box = round(money_box + (per_day - today), 2)
        sql = f'UPDATE `{month}_money_box` SET balance="{money_box}";'
        res = my.execute_sql(sql)
        my.close()


def scheduled_update():
    schedule.every().day.at("23:59").do(money_box_counter)
    while True:
        schedule.run_pending()
        time.sleep(60)
