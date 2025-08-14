from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence, Union
import asyncio

from psycopg2.extras import execute_values

from db.postgres import PostgresDB
from utils.logger import get_logger

logger = get_logger(__name__)


# --------------------------------
# 1) Lightweight schema model
# --------------------------------
@dataclass(slots=True)
class PostRecord:
    """
    Minimal schema for jsonplaceholder posts.
    Using dataclass (with __slots__) for:
     - type hints
     -low memory footprint
     -basic runtime validation (custom from_dict)
    """

    id: int
    title: str
    body: str
    user_id: Optional[int] = field(default=None)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "PostRecord":
        """
        Coerce & validate
        :param d:
        :return:
        """

        try:
            """ Accept either 'userId' or 'user_id """
            raw_user_id = d.get("user_id", d.get("userId"))
            return PostRecord(
                id=int(d["id"]),
                title=str(d["title"]),
                body=str(d["body"]),
                user_id=int(raw_user_id) if raw_user_id is not None else None,
            )
        except KeyError as e:
            raise ValueError(f"Missing required key: {e}") from e
        except (TypeError, ValueError) as e:
            raise ValueError(f"Bad field types: {e}") from e


# -----------------------------------------
# 2) Processor (sync + async)
# -----------------------------------------

class DataProcessor:
    """
    Enterprise-grade processor:
    - Validate & normalize raw data -> PostRecord(s)
    - Ensures table exists
    - Bulk upserts in batches with ON CONFLICT
    - Sync API + async wrapper
    """

    def __init__(
            self,
            table_name: str = 'posts',
            batch_size: int = 500,
            db: Optional[PostgresDB] = None,
    ) -> None:
        self.table_name = table_name
        self.batch_size = batch_size
        self.db = db or PostgresDB()  # lazy connect via PostgresDB

    # --------------- Public API ---------------

    def process(self,
                data: Union[Dict[str, Any], List[Dict[str, Any]]]
                ) -> List[PostRecord]:
        """
        Validate & normalize raw data into a list of PostRecord.
        Accepts a single dict or a list of dicts.
        :param data:
        :return:
        """

        logger.info("Processing data ...")
        records: List[PostRecord] = []

        if isinstance(data, dict):
            try:
                records.append(PostRecord.from_dict(data))
            except ValueError as v:
                logger.warning(f"Skipping bad records: {v}")
        elif isinstance(data, list):
            for idx, item in enumerate(data):
                try:
                    records.append((PostRecord.from_dict(item)))
                except ValueError as e:
                    # Skip bad rows but keep going: log with index for traceability
                    logger.warning(f"Skipping bad record ar index{idx}:{e}")
        else:
            logger.warning("Unexpected payload type: expected dict or list of dicts.")
            return []

        logger.info(f"Validated {len(records)} records.")
        return records

    async def process_async(self,
                            data: Union[Dict[str, Any], List[Dict[str, Any]]]
                            ) -> List[PostRecord]:

        """
        Async-friendly wrapper (runs validation in a a worker thread)
        Useful if upstream is async and you want to avoid blocking loop
        """

        return await asyncio.to_thread(self.process, data)

    def save_to_db(self, records: Sequence[PostRecord]) -> None:

        """
        Create table if needed, then upsert in batches using execute_values.
        Idempotent: primary key on id + ON CONFLICT DO UPDATE for title/body/user_id.
        """
        if not records:
            logger.info("No records to save.")
            return

        logger.info(f"Saving {len(records)} record(s) to database (batch_size={self.batch_size})...")
        self._ensure_table()

        # Prepare tuples for bulk insert
        rows = [
            (r.id, r.title, r.body, r.user_id)
            for r in records
        ]

        columns = ("id", "title", "body", "user_id")  # must match table cols
        insert_sql = f"""
                    INSERT INTO {self.table_name} ({", ".join(columns)})
                    VALUES %s
                    ON CONFLICT (id)
                    DO UPDATE SET
                        title = EXCLUDED.title,
                        body = EXCLUDED.body,
                        user_id = EXCLUDED.user_id;
                """

        # Bulk in batches
        for chunk in _chunks(rows, self.batch_size):
            try:
                with self.db.cursor() as cur:
                    execute_values(
                        cur,
                        insert_sql,
                        chunk,
                        template="(%s, %s, %s, %s)",
                        page_size=min(len(chunk), 1000),
                    )
                    # commit handled by PostgresDB.cursor() context manager
                logger.debug(f"Upserted {len(chunk)} record(s).")
            except Exception:
                # PostgresDB handles rollback; we add context to logs here
                logger.exception("Failed to upsert batch.")
                raise

        logger.info("✅ Save completed.")

    async def save_to_db_async(self, records: Sequence[PostRecord]) -> None:
        """
        Async-friendly wrapper (runs DB save in a worker thread).
        """
        await asyncio.to_thread(self.save_to_db, records)

    # ---------- Internal helpers ----------

    def _ensure_table(self) -> None:
        """
        Create the table if it doesn't exist (bootstrap).
        In production, a migration tool is preferred (Alembic/Flyway).
        """
        ddl = f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id      BIGINT PRIMARY KEY,
                    title   TEXT NOT NULL,
                    body    TEXT NOT NULL,
                    user_id BIGINT NULL
                );
                """
        try:
            with self.db.cursor() as cur:
                cur.execute(ddl)
            logger.debug(f"Ensured table exists: {self.table_name}")
        except Exception:
            logger.exception("Failed to ensure table exists.")
            raise


# -----------------------------
# 3) Utility: batch chunking
# -----------------------------
def _chunks(seq: Sequence[Any], size: int) -> Iterable[Sequence[Any]]:
    """Yield fixed-size chunks from a sequence (last chunk may be smaller)."""
    if size <= 0:
        yield seq
        return
    for i in range(0, len(seq), size):
        yield seq[i: i + size]
