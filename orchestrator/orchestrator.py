from __future__ import annotations

import argparse
import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import yaml

from ingestion.sync_ingestor import SyncIngestor
from ingestion.async_ingestor import AsyncIngestor
from processing.processor import DataProcessor
from orchestrator.event_store import EventStore, IngestionEvent
from orchestrator.visualize import mermaid_from_config, write_mermaid
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass(slots=True)
class PipelineConfig:
    name: str
    enabled: bool
    mode: str  # "sync" | "async"
    base_url: str
    table: str
    batch_size: int = 500
    # sync-specific
    endpoint: Optional[str] = None
    # async-specific
    url_pattern: Optional[str] = None
    id_range: Optional[Dict[str, int]] = None


def load_config(path: str) -> Dict[str, Any]:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def parse_pipelines(cfg: Dict[str, Any]) -> List[PipelineConfig]:
    items = []
    for p in cfg.get("pipelines", []):
        items.append(PipelineConfig(**p))
    return items


async def run_pipeline_async(p: PipelineConfig, store: EventStore) -> str:
    """
    Return final status string: SUCCESS | FAILED
    """
    start = datetime.utcnow()
    store.log(IngestionEvent(pipeline=p.name, status="RUNNING", started_at=start))

    try:
        processor = DataProcessor(table_name=p.table, batch_size=p.batch_size)

        if p.mode == "sync":
            # Sync mode can still live in async orchestrator via to_thread
            def _run_sync() -> int:
                ing = SyncIngestor()
                url = f"{p.base_url}{p.endpoint}"
                raw = ing.fetch(url)
                recs = processor.process(raw)
                processor.save_to_db(recs)
                return len(recs)

            count = await asyncio.to_thread(_run_sync)

        elif p.mode == "async":
            # Build URL list from pattern and range
            if not (p.url_pattern and p.id_range):
                raise ValueError(f"{p.name}: async pipeline requires url_pattern and id_range")
            urls = [
                f"{p.base_url}{p.url_pattern.replace('{id}', str(i))}"
                for i in range(p.id_range["start"], p.id_range["end"] + 1)
            ]
            ing = AsyncIngestor(urls)
            raw_list = await ing.run()
            raw = [r for r in raw_list if r]
            recs = await processor.process_async(raw)
            await processor.save_to_db_async(recs)
            count = len(recs)

        else:
            raise ValueError(f"{p.name}: invalid mode {p.mode}")

        store.log(IngestionEvent(
            pipeline=p.name, status="SUCCESS",
            started_at=start, finished_at=datetime.utcnow(),
            records=count
        ))
        return "SUCCESS"

    except Exception as e:
        logger.exception(f"[{p.name}] failed.")
        store.log(IngestionEvent(
            pipeline=p.name, status="FAILED",
            detail=str(e), started_at=start, finished_at=datetime.utcnow(),
        ))
        return "FAILED"


async def run_all(cfg_path: str) -> None:
    cfg = load_config(cfg_path)
    pipelines = [p for p in parse_pipelines(cfg) if p.enabled]

    store = EventStore()
    store.ensure_table()

    # Run all enabled pipelines concurrently (safe: mix of asyncio + threads)
    results = await asyncio.gather(*(run_pipeline_async(p, store) for p in pipelines), return_exceptions=False)

    # Build a status map for DAG rendering
    status_map = {pipelines[i].name: results[i] for i in range(len(pipelines))}
    mermaid = mermaid_from_config(cfg, status_map)
    write_mermaid(mermaid, "docs/ingestion_dag.md")


def main() -> None:
    parser = argparse.ArgumentParser(description="Config-driven ingestion orchestrator")
    parser.add_argument("--config", default="configs/pipelines.yaml", help="Path to YAML config")
    args = parser.parse_args()
    asyncio.run(run_all(args.config))


if __name__ == "__main__":
    main()
