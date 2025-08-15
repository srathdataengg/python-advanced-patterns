import argparse
import asyncio
from ingestion.sync_ingestor import SyncIngestor
from ingestion.async_ingestor import AsyncIngestor
from processing.processor import DataProcessor
from configs.config import API_URLS
from utils.logger import get_logger

logger = get_logger(__name__)


def run_sync_pipeline():
    logger.info("Running Sync Ingestion Pipeline")
    ingestor = SyncIngestor(API_URLS)
    data = ingestor.ingest_all()
    logger.info(f"Sync ingestion complete. {len(data)} datasets retrieved.")

    processor = DataProcessor()
    processed = processor.process(data)
    logger.info(f"Processing complete. {len(processed)} datasets processed.")


async def run_async_pipeline():
    logger.info("Running Async Ingestion Pipeline")
    ingestor = AsyncIngestor(API_URLS)
    data = await ingestor.ingest_all()
    logger.info(f"Async ingestion complete. {len(data)} datasets retrieved.")

    processor = DataProcessor()
    processed = processor.process(data)
    logger.info(f"Processing complete. {len(processed)} datasets processed.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run Data Ingestion Pipeline")
    parser.add_argument(
        "--mode",
        choices=["sync", "async"],
        default="sync",
        help="Choose ingestion mode",
    )
    args = parser.parse_args()

    if args.mode == "sync":
        run_sync_pipeline()
    else:
        asyncio.run(run_async_pipeline())
