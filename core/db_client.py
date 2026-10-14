# ---------------- core/db_client.py ----------------
import oracledb

class DBClient:
    def __init__(self, user, password, dsn):
        self.user = user
        self.password = password
        self.dsn = dsn
        self.conn = None
        self.pool = self.get_pool()

    def get_pool(self):
        pool = oracledb.create_pool(
            user=self.user,
            password=self.password,
            dsn=self.dsn,
            min=2,
            max=10,
            increment=1,
            timeout=60
        )
        return pool

    def connect(self):
        self.conn = oracledb.connect(user=self.user, password=self.password, dsn=self.dsn)

    def execute_select(self, sql, bind_vars=None):
        with self.pool.acquire() as conn:
            with conn.cursor() as cursor:
                if bind_vars:
                    cursor.execute(sql, bind_vars)
                else:
                    cursor.execute(sql)
                cols = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                return rows, cols

    def execute_dml(self, sql, bind_vars):
        with self.pool.acquire() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, bind_vars)
                return cursor.rowcount

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()

   