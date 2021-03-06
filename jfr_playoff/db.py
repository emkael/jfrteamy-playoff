import sys

from jfr_playoff.logger import PlayoffLogger


class PlayoffDB(object):

    db_cursor = None
    DATABASE_NOT_CONFIGURED_WARNING = 'database not configured'

    def __init__(self, settings):
        reload(sys)
        sys.setdefaultencoding("latin1")
        import mysql.connector
        self.database = mysql.connector.connect(
            user=settings['user'],
            password=settings['pass'],
            host=settings['host'],
            port=settings.get('port', 3306))
        PlayoffLogger.get('db').info('db settings: %s', settings)
        self.db_cursor = self.database.cursor(buffered=True)

    def get_cursor(self):
        return self.db_cursor

    def __execute_query(self, db_name, sql, params):
        PlayoffLogger.get('db').info(
            'query (%s): %s %s', db_name, sql.replace('\n', ' '), params)
        self.db_cursor.execute(sql.replace('#db#', db_name), params)

    def fetch(self, db_name, sql, params):
        import mysql.connector
        try:
            self.__execute_query(db_name, sql, params)
            row = self.db_cursor.fetchone()
            return row
        except mysql.connector.Error as e:
            PlayoffLogger.get('db').error(str(e))
            raise IOError(e.errno, str(e), db_name)

    def fetch_all(self, db_name, sql, params):
        import mysql.connector
        try:
            self.__execute_query(db_name, sql, params)
            results = self.db_cursor.fetchall()
            return results
        except mysql.connector.Error as e:
            PlayoffLogger.get('db').error(str(e))
            raise IOError(
                message=str(e), filename=db_name,
                errno=e.errno, strerror=str(e))
