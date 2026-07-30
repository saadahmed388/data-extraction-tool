# ---------------- core/db_client.py ----------------
import oracledb
from decimal import Decimal

class DBClient:
    def __init__(self, user, password, dsn):
        self.user = user
        self.password = password
        self.dsn = dsn
        self.conn = None

    def connect(self):
        self.conn = oracledb.connect(user=self.user, password=self.password, dsn=self.dsn)
    
    def execute_select(self, sql, bind_vars=None):
        cursor = self.conn.cursor()
        try:
            if bind_vars:
                cursor.execute(sql, bind_vars)
            else:
                cursor.execute(sql)
            cols = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return rows, cols
            
        finally:
            cursor.close()

    def execute_dml(self, sql, bind_vars):
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql, bind_vars)
            return cursor.rowcount
        finally:
            cursor.close()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()

