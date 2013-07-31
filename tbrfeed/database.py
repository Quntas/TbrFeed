import dj_database_url
import psycopg2

class Connection:
    def __init__(self):
        config = dj_database_url.config()
        self.conn = psycopg2.connect(dbname=config["NAME"], user=config["USER"], password=config["PASSWORD"], host=config["HOST"], port=config["PORT"])

    def __enter__(self):
        return self.conn.cursor()

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self.conn.rollback()
        else:
            self.conn.commit()
        self.conn.close()
