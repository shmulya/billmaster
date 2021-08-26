from modules.mysql_collector import MysqlCollector
from yaml import load, Loader
import datetime
import re


config = load(open('config.yml', 'r').read(), Loader=Loader)


def put(data):
    my = MysqlCollector(config['mysql_host'], config['mysql_username'],
                        config['mysql_password'], config['mysql_database'])
    datestr = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m')
    data.update({'date': datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')})
    res = my.insert(datestr, data)
    my.close()
    return res


def allsum():
    month = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m')
    today = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
    my = MysqlCollector(config['mysql_host'], config['mysql_username'],
                        config['mysql_password'], config['mysql_database'])
    cols = ['food', 'transp', 'health', 'home',
            'smoke', 'cat', 'other', 'alco', 'etc']
    sums = {}
    # подсчёт трат за месяц по категориям
    f_cols = [f'SUM({category})' for category in cols]
    res = my.select(month, cols=f_cols)
    if res['status'] is not True:
        my.close()
        return res
    else:
        for cat, value in res['data'].items():
            sums[re.search('\((.*)\)', cat).group(1)] = float(str(value))
    # подсчёт трат за день
    per_day = 0
    res = my.select(month, cols=f_cols, where=f'date="{today}"')
    if res['status'] is not True:
        my.close()
        return res
    else:
        for value in res['data'].values():
            try:
                per_day = per_day + float(str(value))
            except Exception:
                per_day = 0
    sum_per_month = 0
    for v in sums.values():
        sum_per_month = sum_per_month + v
    sums['all'] = sum_per_month
    # подсчёт баланса
    if sums != {}:
        res = my.select(f'{month}_money')
        if res['status'] is not True:
            my.close()
            return res
        else:
            money = res['data']
            sums['available'] = float(str(money['available']))
            sums['mandatory'] = float(str(money['mandatory']))
            sums['spending'] = round(sums['available'] - sums['mandatory'], 2)
            sums['per_day'] = round(sums['spending'] / 30, 2)
            sums['balance'] = round(sums['spending'] - sums['all'], 2)
            sums['spending_today'] = round(per_day, 2)
            sums['remain_today'] = round(sums['per_day'] - sums['spending_today'], 2)
            # Получение баланса из копилки
            res = my.select(f'{month}_money_box')
            if res['status'] is not True:
                sums['money_box'] = None
            else:
                sums['money_box'] = float(str(res['data']['balance']))
            my.close()
            return {'status': True, 'data': sums}


def report(data):
    result = []
    month = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m')
    my = MysqlCollector(config['mysql_host'], config['mysql_username'],
                        config['mysql_password'], config['mysql_database'])
    res = my.select(month, where=f'date BETWEEN "{data["from"]}" AND "{data["to"]}"')
    my.close()
    if res['status'] is not True:
        return res
    else:
        if type(res['data']) is list():
            for operation in res['data']:
                rawjson = {}
                for col, val in operation.items():
                    if val != 0 and type(val) is datetime.date:
                        rawjson.update({col: datetime.datetime.strftime(val, '%Y-%m-%d')})
                    elif val != 0 and type(val) is not datetime.date:
                        rawjson.update({col: float(str(val))})
                result.append(rawjson)
        else:
            rawjson = {}
            for col, val in res['data'].items():
                if val != 0 and type(val) is datetime.date:
                    rawjson.update({col: datetime.datetime.strftime(val, '%Y-%m-%d')})
                elif val != 0 and type(val) is not datetime.date:
                    rawjson.update({col: float(str(val))})
            result.append(rawjson)
        return {'status': True, 'data': result}


def money_box_counter():
    month = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m')
    day_today = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
    my = MysqlCollector(config['mysql_host'], config['mysql_username'],
                        config['mysql_password'], config['mysql_database'])
    cols = ['food', 'transp', 'health', 'home',
            'smoke', 'cat', 'other', 'alco', 'etc']
    # подсчёт трат за день
    f_cols = [f'SUM({category})' for category in cols]
    per_day = 0
    today = 0
    res = my.select(month, cols=f_cols, where=f'date="{day_today}"')
    if res['status'] is not True:
        my.close()
        return res
    else:
        for value in res['data'].values():
            try:
                today = today + float(str(value))
            except Exception:
                today = 0
    res = my.select(f'{month}_money')
    if res['status'] is not True:
        my.close()
        return res
    else:
        money = res['data']
        available = float(str(money['available']))
        mandatory = float(str(money['mandatory']))
        spending = round(available - mandatory, 2)
        per_day = round(spending / 30, 2)
        res = my.select(f'{month}_money_box')
        if res['status'] is not True:
            my.close()
            return res
        else:
            money_box = float(str(res['data']['balance']))
            # новый баланс копилки
            money_box = round(money_box + (per_day - today), 2)
            res = my.update(f'{month}_money_box', {'balance': money_box})
            my.close()
            return res
