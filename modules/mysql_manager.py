import mysql.connector
import datetime


class mysqlManager:

    def __init__(self, server, username, passwd, db):
        self.my = mysql.connector.connect(user=username, password=passwd, host=server,
                                          database=db)
        self.cursor = self.my.cursor()

    def sqlinsert_from_json(self, data, table):
        fields = ''
        values = ''
        for k, v in data.items():
            fields = fields + f'`{k}`, '
            values = values + f'"{v}", '
        fields = fields[:-2]
        values = values[:-2]
        datestr = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
        sql = f'INSERT INTO `{table}` (`date`, {fields}) VALUES ("{datestr}", {values});'
        return sql

    def execute_sql(self, sql):
        try:
            self.cursor.execute(sql)
        except Exception as err:
            return {'status': False, 'data': str(err)}
        else:
            try:
                rows = self.cursor.fetchall()
            except Exception:
                rows = []
            self.my.commit()
            return {'status': True, 'data': rows}

    def close(self):
        self.my.close()