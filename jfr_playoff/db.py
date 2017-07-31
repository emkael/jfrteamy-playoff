import mysql.connector

class PlayoffDB(object):

    db_cursor = None

    def __init__(self, settings):
        self.database = mysql.connector.connect(
            user=settings['user'],
            password=settings['pass'],
            host=settings['host'],
            port=settings['port']
        )
        self.db_cursor = self.database.cursor(buffered=True)

    def fetch(self, db, sql, params):
        self.db_cursor.execute(sql.replace('#db#', db), params)
        row = self.db_cursor.fetchone()
        return row
