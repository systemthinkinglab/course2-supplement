# Course 2 Supplement — Content & Information Systems

**Systems Thinking in the AI Era II**

This repository contains the discovery labs and challenge templates for [Course 2: Content & Information Systems](https://systemthinkinglab.ai/course-2).

## What's in here

```
course2-supplement/
├── building_blocks/        Shared building block reference implementations
│   ├── building_blocks.py  Service, Worker, FileStore, KeyValueStore, Queue,
│   │                       RelationalDB, VectorDB (the 7 universal building blocks)
│   └── external_entities.py  User, External Service, Time
│
├── labs/course2/           Hands-on discovery labs
│   ├── lab1_service_file_store.py   Service + File Store — Media Handling
│   └── lab2_service_kvs.py          Service + Key-Value Store — Caching
│
└── challenges/course2/     Technical Design Document templates
    ├── part1-mvp-foundation.md          Challenge Part 1 template
    ├── part2-viral-content-crisis.md    Challenge Part 2 template
    └── part3-ai-personalization.md      Challenge Part 3 template
```

## Quick start

You need Python 3.8 or higher. No third-party packages are required — the labs use only the standard library.

```bash
git clone https://github.com/systemthinkinglab/course2-supplement.git
cd course2-supplement
python3 labs/course2/lab1_service_file_store.py
```

## Running the labs

Each lab is interactive and self-contained. You'll be guided through four progressive experiments with reflection questions and educational feedback after each one.

### Lab 1 — Service + File Store (Media Handling)

```bash
python3 labs/course2/lab1_service_file_store.py
```

Four experiments build deep intuition for handling user-uploaded media:
1. **Naive storage** — photos as BLOBs in a Relational Database (feel the pain)
2. **Service + File Store split** — bytes in File Store, metadata in DB (feel the relief)
3. **Media processing pipeline** — Queue + Worker for async thumbnail generation
4. **CDN integration** — edge caching for global delivery

```bash
# Run a single experiment directly
python3 labs/course2/lab1_service_file_store.py 2

# Skip the typewriter effect (faster runs)
python3 labs/course2/lab1_service_file_store.py --instant
```

### Lab 2 — Service + Key-Value Store (Caching)

```bash
python3 labs/course2/lab2_service_kvs.py
```

Four experiments build deep intuition for caching:
1. **Database-only reads** — feel the bottleneck under repeat traffic
2. **Cache-aside pattern** — watch hit rates climb and DB load collapse
3. **Invalidation strategies** — TTL vs write-through, with real stale data
4. **Thundering herd** — simulate the production nightmare, then fix it with coalescing

```bash
# Run a single experiment directly
python3 labs/course2/lab2_service_kvs.py 4

# Skip the typewriter effect (faster runs)
python3 labs/course2/lab2_service_kvs.py --instant
```

## Challenge templates

The three Technical Design Document templates in `challenges/course2/` are scaffolds for the Course 2 Capstone Challenge — designing a news aggregation platform.

- **Part 1: MVP Foundation** — 5 requirements, design the core platform
- **Part 2: Viral Content Crisis** — evolve to handle 100x traffic spikes
- **Part 3: AI Personalization** — layer in semantic search and personalized feeds

Download the template you're working on, fill in each section using **building block names** (Service, Queue, Worker, Key-Value Store, File Store, Relational Database, Vector Database, External Service), and submit through the challenge form on the course site.

## Building block language

These labs and challenges teach you to think in **building blocks** rather than specific technologies. Use names like `Key-Value Store` instead of `Redis`, `File Store` instead of `S3`, `External Service` instead of `OpenAI API`. The pattern is what matters; technology is implementation.

## Course site

Full course at [systemthinkinglab.ai/course-2](https://systemthinkinglab.ai/course-2).

## License

See [LICENSE](LICENSE).
