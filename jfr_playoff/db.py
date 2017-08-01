import mysql.connector


class PlayoffDB(object):

    db_cursor = None

    def __init__(self, settings):
        self.database = mysql.connector.connect(
            user=settings['user'],
            password=settings['pass'],
            host=settings['host'],
            port=settings['port'])
        self.db_cursor = self.database.cursor(buffered=True)

    def get_cursor(self):
        return self.db_cursor

    def fetch(self, db_name, sql, params):
        self.db_cursor.execute(sql.replace('#db#', db_name), params)
        row = self.db_cursor.fetchone()
        return row
