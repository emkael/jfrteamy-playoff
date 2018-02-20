import sys

import mysql.connector


class PlayoffDB(object):

    db_cursor = None
    DATABASE_NOT_CONFIGURED_WARNING = 'WARNING: database not configured'

    def __init__(self, settings):
        reload(sys)
        sys.setdefaultencoding("latin1")
        self.database = mysql.connector.connect(
            user=settings['user'],
            password=settings['pass'],
            host=settings['host'],
            port=settings['port'])
        self.db_cursor = self.database.cursor(buffered=True)

    def get_cursor(self):
        return self.db_cursor

    def __execute_query(self, db_name, sql, params):
        self.db_cursor.execute(sql.replace('#db#', db_name), params)

    def fetch(self, db_name, sql, params):
        self.__execute_query(db_name, sql, params)
        row = self.db_cursor.fetchone()
        return row

    def fetch_all(self, db_name, sql, params):
        self.__execute_query(db_name, sql, params)
        results = self.db_cursor.fetchall()
        return results
