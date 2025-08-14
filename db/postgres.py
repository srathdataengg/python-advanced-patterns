import os

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import OperationalError, DatabaseError
from utils.logger import get_logger
from contextlib import contextmanager
import os

logger = get_logger(__name__)


class PostgresDB:
    def __init__(self, host="localhost", dbname="mydb", user="postgres", password="postgres", port=5432):
        self.conn = None
        self.config = {
            "host": host or os.getenv("DB_HOST", "localhost"),
            "dbname": dbname or os.getenv("DB_NAME", "ingestiondb"),
            "user": user or os.getenv("DB_USER", "ingestionuser"),
            "password": password or os.getenv("DB_PASSWORD", "postgres"),
            "port": port or int(os.getenv("DB_PORT", 5432))
        }

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logger.error(f"Rolling back transition due to: {exc_val}")
            self.conn.rollback()
        self.close()

    def connect(self):
        """Establish connection to the database."""
        if not self.conn:
            try:
                self.conn = psycopg2.connect(**self.config, cursor_factory=RealDictCursor)
                logger.info("Connected to Postgres DB.")
            except OperationalError as e:
                logger.error(f" Operational error connecting to Postgres: {e} ")
                raise

            except Exception as e:
                logger.error(f"Failed to connect to Postgress: {e}")
                raise

    @contextmanager
    def get_cursor(self):
        """Context manager for DB cursor."""
        if not self.conn:
            self.connect()
        try:
            with self.conn.cursor() as cur:
                yield cur
                self.conn.commit()
        except DatabaseError as e:
            self.conn.rollback()
            logger.error(f"❌ Database error: {e}")
            raise
        except Exception as e:
            self.conn.rollback()
            logger.error(f"❌ Unexpected error: {e}")
            raise

    def execute(self, query, params=None):
        """Execute INSERT/UPDATE/DELETE queries."""
        with self.get_cursor() as cur:
            cur.execute(query, params)

    def fetchall(self, query, params=None):
        """Fetch multiple rows."""
        with self.get_cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()

    def fetchone(self, query, params=None):
        """Fetch single row."""
        with self.get_cursor() as cur:
            cur.execute(query, params)
            return cur.fetchone()

    def close(self):
        """Close connection."""
        if self.conn:
            try:
                self.conn.close()
                logger.info("🔌 Postgres connection closed.")
            except Exception as e:
                logger.warning(f"⚠️ Error closing Postgres connection: {e}")