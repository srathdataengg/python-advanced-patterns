        +------------------+
        | External Sources  |
        | (APIs, Files,     |
        |  Streams, etc.)   |
        +--------+----------+
                 |
         (Sync / Async)
                 v
        +--------+----------+
        | Ingestion Service |
        |-------------------|
        | main.py           |  <-- Entry point (mode: sync / async / multi)
        | base.py           |  <-- Abstract base ingestor (OOP + SOLID)
        | sync_ingestor.py  |  <-- Sync pipeline implementation
        | async_ingestor.py |  <-- Async pipeline implementation
        | retry.py          |  <-- Retry / backoff decorator
        +--------+----------+
                 |
         +-------+--------+
         | Processing     |
         | Layer          |
         | (processor.py) |
         +-------+--------+
                 |
      +----------+-----------+
      | Persistence Layer    |
      |----------------------|
      | postgres.py          |
      | redis_cache.py       |
      +----------+-----------+
                 |
     +-----------+----------+
     | Postgres (DB)        |
     | Redis (Cache / Queue)|
     +----------------------+
