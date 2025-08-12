           ┌─────────────────────────┐
           │       main.py           │
           │  (entrypoint CLI)       │
           └──────────┬──────────────┘
                      │
                      ▼
           ┌─────────────────────────┐
           │   Ingestor (Base)       │
           │ ingestion/base.py       │
           │ - fetch()               │
           │ - process()             │
           └──────────┬──────────────┘
                      │
          ┌───────────┴───────────────┐
          ▼                           ▼
┌────────────────────┐       ┌────────────────────┐
│ SyncIngestor        │       │ AsyncIngestor*     │ (*Phase 2)
│ sync_ingestor.py    │       │ async_ingestor.py  │
│ - fetch API data    │       │ - fetch parallel   │
│ - format data       │       │ - async pipelines  │
└───────────┬─────────┘       └────────────────────┘
            │
            ▼
   ┌────────────────────────┐
   │ Processor              │
   │ processing/processor.py│
   │ - clean & transform    │
   └───────────┬────────────┘
               │
               ▼
   ┌────────────────────────┐
   │ Postgres Layer         │
   │ db/postgres.py         │
   │ - insert rows          │
   └───────────┬────────────┘
               │
               ▼
   ┌────────────────────────┐
   │ Postgres Container      │
   └────────────────────────┘

Phase-2 - Async Ingestion with Redis
------------------------------------
           ┌──────────────────────────┐
           │        main.py           │
           │ --mode async             │
           └───────────┬──────────────┘
                       │
                       ▼
           ┌──────────────────────────┐
           │ AsyncIngestor            │
           │ ingestion/async_ingestor │
           │ - aiohttp + asyncio      │
           │ - multiple API calls     │
           └───────────┬──────────────┘
                       │
        ┌──────────────┴───────────────────┐
        ▼                                  ▼
┌──────────────────────┐          ┌───────────────────────┐
│ Redis Cache Layer    │          │ Processor             │
│ db/redis_cache.py    │          │ processing/processor  │
│ - check before fetch │          │ - clean & transform   │
│ - store fresh data   │          └───────────┬───────────┘
└───────────┬──────────┘                      │
            │                                  ▼
     ┌─────────────┐               ┌────────────────────────┐
     │ External    │               │ Postgres Layer         │
     │ APIs        │               │ db/postgres.py         │
     └─────────────┘               │ - bulk inserts         │
                                    └────────────────────────┘
