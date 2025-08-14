from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Literal
from datetime import datetime

from db.postgres import PostgresDB
from utils.logger import get_logger

logger = get_logger(__name__)

Status = Literal["PENDING", "RUNNING", "SUCCESS", "FAILED"]


@dataclass(slots=True)
class IngestionEvent:
    pipeline: str
    status: Status
    detail: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    records: Optional[int] = None


class EventStore:
    def __init__(self, table_name: str = "ingestion_events", db: Optional[PostgresDB] = None) -> None:
        self.table_name = table_name
        self.db = db or PostgresDB()

    def ensure_table(self) -> None:
        ddl = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            id           BIGSERIAL PRIMARY KEY,
            pipeline     TEXT NOT NULL,
            status       TEXT NOT NULL,
            detail       TEXT NULL,
            started_at   TIMESTAMPTZ NULL,
            finished_at  TIMESTAMPTZ NULL,
            records      BIGINT NULL,
            created_at   TIMESTAMPTZ DEFAULT NOW()
        );
        """
        with self.db.cursor() as cur:
            cur.execute(ddl)
        logger.debug("Ensured ingestion_events table exists.")

    def log(self, evt: IngestionEvent) -> None:
        sql = f"""
        INSERT INTO {self.table_name}
        (pipeline, status, detail, started_at, finished_at, records)
        VALUES (%s, %s, %s, %s, %s, %s);
        """
        with self.db.cursor() as cur:
            cur.execute(sql, (evt.pipeline, evt.status, evt.detail, evt.started_at, evt.finished_at, evt.records))
        logger.info(f"[{evt.pipeline}] status={evt.status} records={evt.records or 0}")
