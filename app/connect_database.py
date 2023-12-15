from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool
from app.settings import DB

class ConnectModel:
    _connection_pools = {}

    def __init__(self, db_alias=None):
        if not db_alias:
            db_alias = 'default'
        self.db_alias = db_alias
        self.db = DB.get(db_alias, {})
        self.connection_pool = self._get_connection_pool()

    def _get_connection_pool(self):
        if self.db_alias not in ConnectModel._connection_pools:
            ConnectModel._connection_pools[self.db_alias] = ThreadedConnectionPool(minconn=1, maxconn=10, **self.db)
        return ConnectModel._connection_pools[self.db_alias]
    
    # def close_connection(self):
    #   self.connection_pool.closeall()

    def _get_connection(self):
        return self.connection_pool.getconn()
    
    def _put_connection(self, conn):
        return self.connection_pool.putconn(conn)
    
    def commit_connect(self):
        conn = self._get_connnection()
        conn.commit()

    def init_extension(self):
            # SET TIME ZONE 'UTC';
        sql_query = """
            CREATE EXTENSION IF NOT EXISTS unaccent;
        """
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql_query)
                conn.commit()
        except Exception as e:
            conn.rollback()
            raise ValueError(str(e))
        finally:
            self._put_connection(conn)

    def execute_get(self, query, is_list=True):
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor)as cur:
                cur.execute(str(query))
                data = cur.fetchall() if is_list else cur.fetchone()
                return data
        except Exception as e:
            raise ValueError(' %s' % str(e))
        finally:
            self._put_connection(conn)

    def execute_update(self, query, is_commit=True):
        conn = self._get_connection()
        try: 
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(str(query))
                if is_commit:
                    conn.commit()  # Thực hiện commit sau khi thực hiện truy vấn chèn
                return cur.rowcount
        except Exception as e:
            conn.rollback()
            raise ValueError(' %s' % str(e))
        finally:
            self._put_connection(conn)
        
    def execute_insert(self, query, is_commit=True):
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(str(query))
                if is_commit:
                    conn.commit()  # Thực hiện commit sau khi thực hiện truy vấn chèn
                return True
        except Exception as e:
            conn.rollback()
            raise ValueError(' %s' % str(e))
        finally:
            self._put_connection(conn)
    
    def execute_insert_multi(self, query, is_commit=True):
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(str(query))
                if is_commit:
                    conn.commit() # Thực hiện commit sau khi thực hiện truy vấn chèn
                return True
        except Exception as e:
            conn.rollback()
            raise ValueError(' %s' % str(e))
        finally:
            self._put_connection(conn)
    
    def execute_delete(self, query, is_commit=True):
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(str(query))
                if is_commit:
                    conn.commit()  # Thực hiện commit sau khi thực hiện truy vấn chèn
                return cur.rowcount
        except Exception as e:
            conn.rollback()
            raise ValueError(' %s' % str(e))
        finally:
            self._put_connection(conn)