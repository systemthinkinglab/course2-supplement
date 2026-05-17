#!/usr/bin/env python3
# =============================================================================
# Systems Thinking in the AI Era
# https://systemthinkinglab.ai
#
# This code is part of the "Systems Thinking in the AI Era" course series.
# For more information, educational content, and courses, visit:
# https://systemthinkinglab.ai
# =============================================================================

"""
Systems Thinking in the AI Era II: Content & Information Systems
Lesson 8: Service + Key-Value Store Caching Discovery Lab
Interactive Python Application

Four progressive experiments that build deep intuition for caching:
1. Database-only reads (the bottleneck)
2. Cache-aside pattern (the relief)
3. Cache invalidation strategies (TTL vs write-through)
4. Hot keys and the thundering herd
"""

import os
import sys
import time
import random
import tempfile
import shutil
import argparse
import threading
from typing import Optional

# Dual-mode import so this file works in both layouts:
#   1. Monorepo / standalone:  building_blocks.py sits next to this file (sibling import)
#   2. course2-supplement repo: building_blocks/ is a top-level package; we add the
#      repo root to sys.path and import from the package
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
sys.path.insert(0, os.path.dirname(os.path.dirname(script_dir)))

try:
    # Sibling import — works when building_blocks.py is next to this file
    from building_blocks import Service, RelationalDB, KeyValueStore
except ImportError:
    try:
        # Package import — works when building_blocks/ is a top-level package
        from building_blocks.building_blocks import Service, RelationalDB, KeyValueStore
    except ImportError:
        print("Error: Could not import building_blocks module.")
        print("Expected building_blocks.py next to this file, OR building_blocks/ package at repo root.")
        sys.exit(1)


# Constant — every database query in this lab takes this much wall time so the
# user can feel the difference between a hit and a miss without waiting forever.
SIMULATED_DB_LATENCY_S = 0.05  # 50ms per database read


class LabExperience:
    """Interactive lab experience for Lesson 8: Service + Key-Value Store"""

    def __init__(self, student_name: str = "Student"):
        self.student_name = student_name
        self.experiment_times = {}

        self.separator = "=" * 80
        self.mini_separator = "-" * 40

        self.typewriter_speed = 0.03
        self.fast_typewriter_speed = 0.01
        self.instant_print = False

        self.print_lock = threading.Lock()
        self.workspace = tempfile.mkdtemp(prefix="lab2_kvs_")

    # -----------------------------------------------------------------------
    # Print helpers
    # -----------------------------------------------------------------------

    def typewriter_print(self, text: str, speed: Optional[float] = None, end: str = "\n"):
        if self.instant_print:
            print(text, end=end)
            return
        if speed is None:
            speed = self.typewriter_speed
        for char in text:
            print(char, end='', flush=True)
            if char not in [' ', '\n', '\t']:
                time.sleep(speed)
        print(end=end)

    def direct_print(self, text: str, end: str = "\n"):
        with self.print_lock:
            print(text, end=end)

    def print_header(self, text: str, style: str = "main"):
        if style == "main":
            print(f"\n{self.separator}")
            print(f"🎯 {text.upper()}")
            print(self.separator)
        elif style == "sub":
            print(f"\n{self.mini_separator}")
            print(f"▶️  {text}")
            print(self.mini_separator)
        elif style == "experiment":
            print(f"\n{'🧪' * 20}")
            print(f"🧪 EXPERIMENT: {text}")
            print('🧪' * 20)

    def print_experiment(self, text: str):
        self.print_header(text, style="experiment")

    def print_info(self, text: str, indent: int = 0):
        prefix = "  " * indent + "ℹ️ " if indent == 0 else "  " * indent
        for line in text.strip().split('\n'):
            self.typewriter_print(f"{prefix}{line}")

    def print_result(self, text: str):
        self.typewriter_print(f"✅ {text}")

    def print_warning(self, text: str):
        self.typewriter_print(f"⚠️  {text}")

    def wait_for_enter(self, prompt: str = "Press ENTER to continue..."):
        input(f"\n📍 {prompt}")

    def ask_yes_no(self, question: str) -> bool:
        while True:
            response = input(f"\n❓ {question} (yes/no): ").lower().strip()
            if response in ['yes', 'y']:
                return True
            elif response in ['no', 'n']:
                return False
            print("Please answer 'yes' or 'no'")

    def ask_multiple_choice(self, question: str, choices: list, responses: list) -> str:
        print(f"\n💭 REFLECTION QUESTION:")
        print(f"   {question}\n")
        for i, choice in enumerate(choices, 1):
            print(f"   {i}. {choice}")
        while True:
            try:
                choice_num = int(input(f"\n❓ Enter your choice (1-{len(choices)}): ").strip())
                if 1 <= choice_num <= len(choices):
                    break
                print(f"Please enter a number between 1 and {len(choices)}")
            except ValueError:
                print(f"Please enter a valid number between 1 and {len(choices)}")
        selected_choice = choices[choice_num - 1]
        educational_response = responses[choice_num - 1]
        print(f"\n✅ You selected: {selected_choice}")
        print("\n🎯 ", end='')
        self.typewriter_print(educational_response)
        self.wait_for_enter()
        return selected_choice

    # -----------------------------------------------------------------------
    # Shared setup: a small "articles" database
    # -----------------------------------------------------------------------

    def setup_articles_db(self, db_name: str) -> RelationalDB:
        """Seed a fresh DB with 100 articles."""
        db = RelationalDB(db_name, db_path=os.path.join(self.workspace, f"{db_name}.db"))
        db.create_table(
            "articles",
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "title TEXT, body TEXT, version INTEGER"
        )
        for i in range(100):
            db.insert("articles", {
                "title": f"Article {i:03d}",
                "body": f"Lorem ipsum body for article {i}. " * 20,
                "version": 1,
            })
        return db

    def simulated_db_read(self, db: RelationalDB, article_id: int) -> Optional[dict]:
        """A database read that takes a realistic ~50ms (network + query)."""
        time.sleep(SIMULATED_DB_LATENCY_S)
        rows = db.select("articles", where_clause="id = ?", params=[article_id])
        return rows[0] if rows else None

    # -----------------------------------------------------------------------
    # Welcome
    # -----------------------------------------------------------------------

    def run_welcome(self):
        self.print_header("WELCOME TO SYSTEMS THINKING IN THE AI ERA")
        print("\n🎓 Systems Thinking in the AI Era II: Content & Information Systems")
        print("📚 Lesson 8: Service + Key-Value Store Caching Discovery Lab\n")

        self.typewriter_print("Transform from a code writer who hopes the database is fast enough")
        self.typewriter_print("to a system thinker who knows exactly when and how to cache.")

        self.student_name = input("\n\n👤 What's your name? ").strip() or "Student"
        self.typewriter_print(f"\nWelcome, {self.student_name}! Let's discover caching the hard way — by feeling it.")

        self.print_info("""
You're about to experience — not just read about — why every serious
read-heavy system puts a Key-Value Store cache in front of its database.

You'll run four experiments:
1. Database-only reads: feel the bottleneck under load
2. Cache-aside pattern: feel the relief as the cache absorbs traffic
3. Invalidation strategies: TTL vs write-through, with real stale data
4. Hot keys and the thundering herd: simulate the production nightmare,
   then implement the fixes

After each experiment, three multiple-choice reflection questions with
immediate educational feedback.
""")
        self.wait_for_enter("Ready to discover? Press ENTER to begin!")

    # =======================================================================
    # EXPERIMENT 1 — Database-only reads (the bottleneck)
    # =======================================================================

    def experiment_1_db_bottleneck(self):
        self.print_experiment("1 - DATABASE-ONLY READS (THE BOTTLENECK)")

        self.print_info("""
In this experiment, every read hits the Relational Database directly.
No cache. Every user requesting the same popular article triggers a
full database query, paying ~50ms each time.

You'll simulate 200 read requests, with 80% targeting the same hot
article (a viral homepage post) and 20% random. Watch the total time
add up and the DB query count climb.
""")
        self.wait_for_enter()

        db = self.setup_articles_db("bottleneck_db")
        service = Service("article_service_no_cache")

        @service.route("/article")
        def handle(data):
            return self.simulated_db_read(db, data["article_id"])

        # Workload: 200 reads, 80% on the hot article, 20% random
        total_requests = 200
        hot_article_id = 7
        latencies = []
        start_time = time.time()

        self.typewriter_print("\n🚀 Sending 200 reads (80% on the hot article)...\n")
        for i in range(total_requests):
            article_id = hot_article_id if random.random() < 0.8 else random.randint(1, 100)
            t0 = time.time()
            service.handle_request("/article", data={"article_id": article_id})
            latencies.append(time.time() - t0)
            if (i + 1) % 50 == 0:
                self.direct_print(f"   📊 Completed {i+1}/{total_requests} reads")

        total_time = time.time() - start_time
        self.experiment_times['experiment_1'] = total_time

        db_query_count = db.get_stats()['query_count']
        avg_latency_ms = (sum(latencies) / len(latencies)) * 1000

        print(f"\n📊 No-Cache Statistics:")
        print(f"   📥 Total requests served: {total_requests}")
        print(f"   🗄️  Database queries executed: {db_query_count}")
        print(f"   ⏱️  Average response time: {avg_latency_ms:.0f}ms")
        print(f"   ⏱️  Total elapsed: {total_time:.1f}s")

        self.print_warning(
            f"Every single request hit the database — even though {int(total_requests*0.8)} "
            f"of them were asking for the EXACT SAME article."
        )

        self.print_header("EXPERIMENT 1 REFLECTIONS", style="sub")

        self.ask_multiple_choice(
            "Why is hitting the database for every read wasteful in this scenario?",
            [
                "Because the same hot article was requested repeatedly, so the database did identical work over and over",
                "Because the database connection itself is slow regardless of what's being queried",
                "Because 200 requests is too many for any database to handle",
            ],
            [
                "Exactly. The hot article was requested ~160 times. The first request had to hit the database — fine. But requests 2-160 did identical work for identical results. That's pure waste. A cache lets you do that work once and reuse the result.",
                "Database connection overhead is real, but it's not the main issue here. Even with an instant connection, doing the same query 160 times wastes the database's time. The issue is repeated work for the same data, not the network.",
                "200 requests is nothing for a modern database. Production systems handle millions of requests per second. The waste here isn't the volume — it's that 160 of those requests asked for the EXACT same row that the database had just served seconds ago.",
            ],
        )

        self.ask_multiple_choice(
            "What happens to this system if traffic suddenly spikes 10x to 2,000 requests?",
            [
                "The database becomes a bottleneck — queries queue up, latencies climb, eventually the database refuses connections",
                "Nothing changes — databases scale infinitely",
                "Response times improve because the database 'warms up'",
            ],
            [
                "Correct. Databases have finite connection pools and finite query throughput. Under spike load with no cache, every additional request piles up on the database. This is the standard cause of cascading outages on read-heavy systems — and exactly the failure mode Challenge Part 2 (the viral content crisis) asks you to design around.",
                "Databases absolutely have limits. Connection pools, lock contention, disk I/O — all finite. Under a 10x spike with no cache, response times degrade rapidly and the database can crash entirely. Caching is what prevents this.",
                "Databases don't 'warm up' to handle more load — they have fixed throughput. If anything, more contention slows everything down. The way to handle spike load is to keep requests off the database, which is what caching does.",
            ],
        )

        self.ask_multiple_choice(
            "What building block would solve this efficiently?",
            [
                "A Key-Value Store sitting in front of the database, caching results by article ID",
                "A second copy of the database for redundancy",
                "A Queue between the Service and the database to slow down requests",
            ],
            [
                "Yes. A Key-Value Store keyed by article_id, with the article row as the value. First request misses → query DB → populate cache. Every subsequent request hits the cache in microseconds. You'll feel this transformation in Experiment 2.",
                "A second database (read replica) helps with scaling reads, but it still wastes work. Each replica still serves the same hot article over and over. Caching the result of one query so all 160 readers share it is a much bigger leverage.",
                "A Queue between Service and database would just delay the inevitable. The fundamental problem is doing the same work repeatedly. The fix is to do the work once and reuse the result — that's what a cache does.",
            ],
        )

        if self.ask_yes_no("Ready to feel the relief of cache-aside?"):
            self.experiment_2_cache_aside()

    # =======================================================================
    # EXPERIMENT 2 — Cache-aside pattern
    # =======================================================================

    def experiment_2_cache_aside(self):
        self.print_experiment("2 - CACHE-ASIDE PATTERN (THE RELIEF)")

        self.print_info("""
Now you'll add a Key-Value Store in front of the database. The cache-aside
algorithm is simple:

  1. Check cache for the key
  2. HIT  → return cached value immediately (no DB query)
  3. MISS → query DB, store result in cache, return value

Same workload as Experiment 1. Watch the database query count plummet and
the average latency drop as the cache warms up.
""")
        self.wait_for_enter()

        db = self.setup_articles_db("cached_db")
        cache = KeyValueStore("article_cache", max_size=200)
        service = Service("article_service_cached")

        hits = {"count": 0}
        misses = {"count": 0}

        @service.route("/article")
        def handle(data):
            key = f"article:{data['article_id']}"
            cached = cache.get(key)
            if cached is not None:
                hits["count"] += 1
                return cached
            misses["count"] += 1
            row = self.simulated_db_read(db, data["article_id"])
            if row is not None:
                cache.set(key, row, ttl_seconds=60)
            return row

        total_requests = 200
        hot_article_id = 7
        latencies = []
        hit_rate_progression = []
        start_time = time.time()

        self.typewriter_print("\n🚀 Sending 200 reads through Service + cache + DB...\n")
        for i in range(total_requests):
            article_id = hot_article_id if random.random() < 0.8 else random.randint(1, 100)
            t0 = time.time()
            service.handle_request("/article", data={"article_id": article_id})
            latencies.append(time.time() - t0)
            if (i + 1) % 50 == 0:
                rate = hits["count"] / (i + 1)
                hit_rate_progression.append(rate)
                self.direct_print(
                    f"   📊 {i+1}/{total_requests} reads — "
                    f"hit rate {rate*100:.0f}% — "
                    f"DB queries so far: {db.get_stats()['query_count']}"
                )

        total_time = time.time() - start_time
        self.experiment_times['experiment_2'] = total_time

        avg_latency_ms = (sum(latencies) / len(latencies)) * 1000
        cache_stats = cache.get_stats()

        print(f"\n📊 Cache-Aside Statistics:")
        print(f"   📥 Total requests served: {total_requests}")
        print(f"   ✅ Cache hits: {hits['count']} ({hits['count']/total_requests*100:.0f}%)")
        print(f"   ❌ Cache misses (DB queries): {misses['count']}")
        print(f"   ⏱️  Average response time: {avg_latency_ms:.1f}ms")
        print(f"   ⏱️  Total elapsed: {total_time:.1f}s")
        print(f"   📉 Database query reduction: from 200 → {misses['count']} "
              f"({(1 - misses['count']/200)*100:.0f}% reduction)")

        self.print_result(
            f"Same workload, far less work. Cache absorbed {hits['count']} reads. "
            f"DB only served {misses['count']} unique articles."
        )

        self.print_header("EXPERIMENT 2 REFLECTIONS", style="sub")

        self.ask_multiple_choice(
            "Why did the database query count drop so dramatically?",
            [
                "Because the first request for each article populates the cache, and every subsequent request for the same article skips the database entirely",
                "Because the cache made the database queries faster",
                "Because we sent fewer requests in this experiment",
            ],
            [
                "Exactly. This is the cache-aside pattern. The DB still does the work the first time, but only the first time. The cache absorbs everything after. With 80% of traffic on one hot article, the DB serves it once and the cache serves it ~159 more times.",
                "The cache doesn't make individual database queries faster — it eliminates them entirely. The reason total time dropped is that most reads never reached the database at all.",
                "Same 200 requests in both experiments. The difference is purely that the cache prevented ~80% of those requests from ever needing the database.",
            ],
        )

        self.ask_multiple_choice(
            "What does the 'hit rate' metric tell you about your caching strategy?",
            [
                "What percentage of requests were served from the cache without touching the database — the higher, the better the cache is working",
                "How many requests the cache stored — bigger cache means higher hit rate",
                "Whether the database is healthy",
            ],
            [
                "Right. Hit rate is the single most important caching metric. 90% means 90% of reads bypass the DB. 99% means almost everything is cached. Hit rate depends on your access pattern (Zipfian/hot-content patterns cache beautifully) and your cache size relative to the working set.",
                "Cache size matters but doesn't directly determine hit rate. Hit rate is determined by your access patterns: if everyone reads different things, a bigger cache helps; if everyone reads the same hot content, even a small cache hits constantly.",
                "Database health is one consequence of good caching (the DB stays unloaded), but the hit rate itself measures the cache's effectiveness — how often it satisfied requests without touching the underlying data source.",
            ],
        )

        self.ask_multiple_choice(
            "When does cache-aside provide the biggest win?",
            [
                "When access patterns are skewed — a small number of items are read repeatedly, like trending articles or hot SKUs",
                "When every read is for a different unique item",
                "When the database is already very fast",
            ],
            [
                "Exactly. Read-heavy systems with Zipfian access patterns — news front pages, e-commerce hot products, popular search terms — get massive leverage from caching because the cache absorbs a huge percentage of traffic. This is why every content platform caches aggressively.",
                "When every read is unique (no repetition), caching adds overhead without benefit because nothing gets reused. Caching only helps when the same data is requested multiple times — which is true for most real workloads, but not all.",
                "Even fast databases have finite throughput. Caching helps regardless of database speed because it eliminates work entirely. But the bigger leverage is on slow paths — caching saves 50ms per hit, which compounds at scale.",
            ],
        )

        if self.ask_yes_no("Ready to wrestle with cache invalidation?"):
            self.experiment_3_invalidation()

    # =======================================================================
    # EXPERIMENT 3 — Invalidation strategies
    # =======================================================================

    def experiment_3_invalidation(self):
        self.print_experiment("3 - INVALIDATION STRATEGIES (TTL vs WRITE-THROUGH)")

        self.print_info("""
"There are only two hard things in computer science: cache invalidation
and naming things." — Phil Karlton

You'll experience why. We'll run the same article through two invalidation
strategies, with a writer updating the article mid-traffic.

  Strategy A: TTL-only — cache entries expire after N seconds. Updates
              that happen between expirations are invisible to readers.

  Strategy B: Write-through — when the article is updated, the cache entry
              is invalidated immediately. Readers see fresh data right away.

Watch how stale data appears (or doesn't) for readers in each strategy.
""")
        self.wait_for_enter()

        db = self.setup_articles_db("invalidation_db")
        cache = KeyValueStore("invalidation_cache", max_size=200)

        article_id = 42

        def read_with_cache_aside(strategy_label: str):
            """Cache-aside read. Logs whether the read was stale."""
            key = f"article:{article_id}"
            cached = cache.get(key)
            if cached is not None:
                return cached, "HIT"
            row = self.simulated_db_read(db, article_id)
            if row is not None:
                cache.set(key, row, ttl_seconds=10)  # short TTL so we see expiration in <30s
            return row, "MISS"

        def update_article(new_body: str, invalidate_cache: bool):
            """Writer updates the article. Optionally invalidates the cache (write-through)."""
            db.update(
                "articles",
                {"body": new_body, "version": int(time.time() * 1000)},
                where_clause="id = ?", params=[article_id]
            )
            if invalidate_cache:
                cache.delete(f"article:{article_id}")

        # --- Strategy A: TTL-only (NO write-through invalidation) ---
        self.print_header("Strategy A: TTL-only (no write-through)", style="sub")
        cache.delete(f"article:{article_id}")  # cold cache
        self.typewriter_print(
            "\n📖 Reader 1 reads → cache miss → DB → cache populated (10s TTL)",
            speed=self.fast_typewriter_speed,
        )
        r1, _ = read_with_cache_aside("A")
        self.typewriter_print(f"   Reader 1 sees body: \"{r1['body'][:50]}...\"",
                              speed=self.fast_typewriter_speed)

        self.typewriter_print("\n✏️  Writer UPDATES the article body... (cache NOT invalidated)",
                              speed=self.fast_typewriter_speed)
        update_article("[BREAKING UPDATE] Article was just edited at " + time.strftime("%H:%M:%S"),
                       invalidate_cache=False)

        self.typewriter_print("\n📖 Reader 2 reads (2 seconds later) → cache HIT → returns STALE data",
                              speed=self.fast_typewriter_speed)
        time.sleep(2)
        r2, status = read_with_cache_aside("A")
        self.typewriter_print(f"   Reader 2 sees body: \"{r2['body'][:50]}...\"  ({status})",
                              speed=self.fast_typewriter_speed)
        if "BREAKING" not in r2["body"]:
            self.print_warning("STALE DATA. Reader 2 missed the update — cache served the old version.")

        self.typewriter_print(
            "\n⏳ Waiting for TTL to expire (10s)...",
            speed=self.fast_typewriter_speed,
        )
        time.sleep(11)
        self.typewriter_print(
            "📖 Reader 3 reads (after TTL expiry) → cache miss → DB → fresh data",
            speed=self.fast_typewriter_speed,
        )
        r3, status = read_with_cache_aside("A")
        self.typewriter_print(f"   Reader 3 sees body: \"{r3['body'][:50]}...\"  ({status})",
                              speed=self.fast_typewriter_speed)

        # --- Strategy B: Write-through invalidation ---
        self.print_header("Strategy B: Write-through invalidation", style="sub")
        cache.delete(f"article:{article_id}")  # cold cache
        self.typewriter_print(
            "\n📖 Reader 1 reads → cache miss → DB → cache populated",
            speed=self.fast_typewriter_speed,
        )
        r1, _ = read_with_cache_aside("B")
        self.typewriter_print(f"   Reader 1 sees body: \"{r1['body'][:50]}...\"",
                              speed=self.fast_typewriter_speed)

        self.typewriter_print(
            "\n✏️  Writer UPDATES the article AND invalidates the cache entry",
            speed=self.fast_typewriter_speed,
        )
        update_article("[ANOTHER UPDATE] Article edited again at " + time.strftime("%H:%M:%S"),
                       invalidate_cache=True)

        self.typewriter_print(
            "\n📖 Reader 2 reads (immediately) → cache MISS → DB → fresh data",
            speed=self.fast_typewriter_speed,
        )
        r2, status = read_with_cache_aside("B")
        self.typewriter_print(f"   Reader 2 sees body: \"{r2['body'][:50]}...\"  ({status})",
                              speed=self.fast_typewriter_speed)
        if "ANOTHER" in r2["body"]:
            self.print_result("FRESH DATA. Write-through invalidation worked — no stale read.")

        self.experiment_times['experiment_3'] = 20  # rough

        self.print_header("EXPERIMENT 3 REFLECTIONS", style="sub")

        self.ask_multiple_choice(
            "Why did Strategy A serve stale data to Reader 2?",
            [
                "The cache entry was still valid (TTL hadn't expired) so the cache returned the old value, unaware the database had changed",
                "The database was too slow to propagate the change",
                "Reader 2's network connection had a glitch",
            ],
            [
                "Right. With TTL-only, the cache has no idea when the underlying data changes. It happily serves whatever it cached, until its timer says 'expire.' Any update between writes and TTL expiration is invisible to readers.",
                "Database writes are immediate — Reader 2 didn't see the update because the cache intercepted the read before it reached the database. The bug is in the cache layer, not the database.",
                "Networks were fine. The cache returned the old data because TTL-only invalidation has no link between the write path and the cache. The cache simply doesn't know an update happened.",
            ],
        )

        self.ask_multiple_choice(
            "What's the trade-off of write-through invalidation (Strategy B)?",
            [
                "It eliminates stale reads, but every write now has to coordinate with the cache, and if that coordination fails the cache and DB get out of sync",
                "It's slower than TTL because invalidation takes time",
                "It only works for read-only data",
            ],
            [
                "Exactly. Write-through gives you freshness in exchange for coupling the write path to the cache. If the cache invalidation fails or partially succeeds (multi-region cache, distributed cache cluster), you can end up with cache and DB disagreeing — a different and sometimes worse problem than stale reads.",
                "Write-through reads are just as fast as TTL reads. The cost is paid by writes, not reads. Writers now have to do two operations (DB write + cache invalidate) instead of one.",
                "Write-through is specifically for read-and-write data — that's where invalidation matters. For pure read-only data, TTL is fine because nothing ever changes anyway.",
            ],
        )

        self.ask_multiple_choice(
            "When is TTL-only invalidation good enough?",
            [
                "When stale data is acceptable for a short window — like view counts, leaderboards, or any data where a few minutes of staleness doesn't hurt the user",
                "Never — write-through is always better",
                "Only for data that never changes",
            ],
            [
                "Right. TTL is simpler and almost always works for data where staleness is tolerable. Use it for analytics dashboards, view counts, popularity rankings, weather data, anything where 'a few minutes ago' is close enough. Reserve write-through for cases where staleness causes actual user harm (auth tokens, financial data, published content).",
                "Write-through is strictly more complex and isn't always worth it. TTL is the right default for most data — only escalate to write-through when correctness demands it.",
                "TTL also works well for data that changes occasionally — you accept the staleness window in exchange for simplicity. Truly never-changing data doesn't even need a cache; it can be a constant.",
            ],
        )

        if self.ask_yes_no("Ready to face the thundering herd?"):
            self.experiment_4_thundering_herd()

    # =======================================================================
    # EXPERIMENT 4 — Hot keys and the thundering herd
    # =======================================================================

    def experiment_4_thundering_herd(self):
        self.print_experiment("4 - HOT KEYS AND THE THUNDERING HERD")

        self.print_info("""
The classic production nightmare:

  1. A popular cached article expires
  2. At that exact moment, 50 simultaneous readers request it
  3. All 50 get cache misses
  4. All 50 hit the database simultaneously
  5. The database, sized for ~10 concurrent reads, falls over

You'll simulate this scenario, then apply two fixes:

  Fix A: TTL jitter — randomize expiration times so entries don't all expire together
  Fix B: Request coalescing — only one request fetches from DB; others wait and share the result
""")
        self.wait_for_enter()

        db = self.setup_articles_db("herd_db")
        cache = KeyValueStore("herd_cache", max_size=200)
        article_id = 99
        cache_key = f"article:{article_id}"
        concurrent_readers = 50

        # ---------------------- Scenario A: vulnerable ----------------------
        self.print_header("Scenario A: vulnerable (no fix)", style="sub")
        # Pre-populate cache then delete to simulate expiration
        cache.set(cache_key, {"body": "cached body"}, ttl_seconds=30)
        cache.delete(cache_key)

        db_query_count_start = db.get_stats()['query_count']

        def vulnerable_read(reader_id: int, results: list):
            cached = cache.get(cache_key)
            if cached is not None:
                results.append("HIT")
                return
            # Cache miss — fall through to DB
            row = self.simulated_db_read(db, article_id)
            cache.set(cache_key, row, ttl_seconds=30)
            results.append("MISS")

        self.typewriter_print(
            f"\n🚀 Releasing {concurrent_readers} concurrent readers at the cache miss moment...",
            speed=self.fast_typewriter_speed,
        )
        results_a = []
        threads = []
        t0 = time.time()
        for i in range(concurrent_readers):
            t = threading.Thread(target=vulnerable_read, args=(i, results_a))
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        elapsed_a = time.time() - t0
        db_queries_a = db.get_stats()['query_count'] - db_query_count_start

        print(f"\n📊 Scenario A Results:")
        print(f"   📥 Concurrent readers: {concurrent_readers}")
        print(f"   🗄️  Database queries triggered: {db_queries_a}  ← stampede!")
        print(f"   ⏱️  Total elapsed: {elapsed_a:.2f}s")
        self.print_warning(
            f"All {db_queries_a} readers piled onto the database simultaneously. "
            f"In production, this is what crashes the database."
        )

        # ---------------------- Scenario B: request coalescing ----------------------
        self.print_header("Scenario B: request coalescing (the fix)", style="sub")
        cache.delete(cache_key)
        db_query_count_start_b = db.get_stats()['query_count']

        # Coalescing: one fetch event per key. The first thread to discover a
        # miss claims the fetch; every other miss-discovering thread waits on
        # the same Event. When the fetcher finishes and populates the cache,
        # it sets the Event; the waiters then read from the warm cache.
        fetch_lock = threading.Lock()
        fetch_done = threading.Event()
        fetcher_chosen = {"flag": False}

        def coalesced_read(reader_id: int, results: list):
            cached = cache.get(cache_key)
            if cached is not None:
                results.append("HIT")
                return
            # Cache miss — decide whether we're the fetcher or a waiter
            with fetch_lock:
                if not fetcher_chosen["flag"]:
                    fetcher_chosen["flag"] = True
                    is_fetcher = True
                else:
                    is_fetcher = False
            if is_fetcher:
                row = self.simulated_db_read(db, article_id)
                cache.set(cache_key, row, ttl_seconds=30)
                fetch_done.set()
                results.append("MISS (fetched)")
            else:
                fetch_done.wait(timeout=2.0)
                results.append("HIT (after wait)")

        self.typewriter_print(
            f"\n🚀 Releasing {concurrent_readers} concurrent readers, this time with coalescing...",
            speed=self.fast_typewriter_speed,
        )
        results_b = []
        threads = []
        t0 = time.time()
        for i in range(concurrent_readers):
            t = threading.Thread(target=coalesced_read, args=(i, results_b))
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        elapsed_b = time.time() - t0
        db_queries_b = db.get_stats()['query_count'] - db_query_count_start_b

        print(f"\n📊 Scenario B Results:")
        print(f"   📥 Concurrent readers: {concurrent_readers}")
        print(f"   🗄️  Database queries triggered: {db_queries_b}  ← coalesced!")
        print(f"   ⏱️  Total elapsed: {elapsed_b:.2f}s")
        self.print_result(
            f"Only {db_queries_b} DB query for {concurrent_readers} readers. "
            f"This is the request-coalescing fix. CDNs implement this at the edge by default."
        )

        # Note about TTL jitter
        self.print_info("""
On TTL jitter: instead of every cache entry expiring at exactly the same
TTL, set each entry's TTL to a randomized value (e.g. TTL ± 30%). This
prevents the synchronized mass-expiration pattern that triggers herds in
the first place. Production caches almost always combine jittered TTLs
with request coalescing.
""")

        self.experiment_times['experiment_4'] = elapsed_a + elapsed_b

        self.print_header("EXPERIMENT 4 REFLECTIONS", style="sub")

        self.ask_multiple_choice(
            "What is the 'thundering herd' problem in caching?",
            [
                "When many concurrent requests for the same key all cache-miss at the same moment and stampede the database simultaneously",
                "When the cache becomes too large to fit in memory",
                "When the database is too small to handle normal load",
            ],
            [
                "Right. The herd specifically happens at cache miss boundaries — when a hot entry expires or gets evicted, all the in-flight readers fall through to the database at once. Even if your DB normally handles 10 concurrent queries comfortably, getting hit with 50 simultaneously can crash it.",
                "Cache memory limits cause evictions but don't directly cause a herd. The herd is specifically the concurrent stampede of cache-missing requests onto the underlying data source. Memory pressure is a separate problem.",
                "Database sizing is one factor, but the herd is a coordination problem, not a capacity problem. Even a well-sized DB can be overwhelmed if 1,000 simultaneous reads all miss the cache at the same moment.",
            ],
        )

        self.ask_multiple_choice(
            "How does request coalescing prevent the herd?",
            [
                "Only one request per key fetches from the database; all other simultaneous requests wait for that fetch to complete, then share the result",
                "It rejects requests until the cache repopulates",
                "It splits the database into smaller pieces",
            ],
            [
                "Exactly. Coalescing turns 50 simultaneous misses into 1 DB query + 49 waiters. The waiters get the same result as the fetcher, just slightly delayed. Total database load is identical to a single request. This is exactly how Varnish, Nginx, and most CDN edge servers handle cache misses internally.",
                "Rejecting requests would shed load but also fails the user — they'd see errors instead of their content. Coalescing keeps every request successful while still protecting the database. Much better outcome.",
                "Sharding the database (splitting it) helps with overall throughput but doesn't solve the herd. Even a sharded database can be overwhelmed if all 50 simultaneous misses go to the same shard for the same hot key.",
            ],
        )

        self.ask_multiple_choice(
            "Why is TTL jitter a useful complement to coalescing?",
            [
                "Jitter prevents synchronized expirations across many keys, so you never get hit with multiple simultaneous herds; coalescing handles whatever herds still occur",
                "Jitter makes the cache faster",
                "Jitter is a replacement for coalescing — you don't need both",
            ],
            [
                "Right. Jitter prevents the *triggering* condition (many keys expiring simultaneously). Coalescing handles the *consequence* (concurrent misses on a single key). Together they cover both ends of the problem. Production caching strategies almost always include both.",
                "Jitter doesn't affect cache speed — it affects the *timing* of expirations. Cache lookups themselves are equally fast with or without jitter.",
                "They solve different problems. Jitter prevents synchronized expiration; coalescing handles concurrent misses once they happen. Even with jitter, a viral spike on a single hot key can still trigger a herd — that's what coalescing handles.",
            ],
        )

        if self.ask_yes_no("Ready to see your discovery summary?"):
            self.show_summary()

    # =======================================================================
    # Summary
    # =======================================================================

    def show_summary(self):
        self.print_header("DISCOVERY SUMMARY")
        self.print_info("""
You've now experienced — not just read about — the canonical caching
patterns that power every read-heavy system on the modern web.

What you discovered:

• Without a cache: every read hits the DB, and the same hot content is
  fetched over and over. Wasteful at any scale; fatal at viral scale.
• Cache-aside: the universal pattern. Check cache → DB on miss → populate
  cache for next time. With realistic access patterns, hit rates of 90%+
  are normal.
• Invalidation has trade-offs: TTL is simple but accepts staleness;
  write-through is fresh but couples writes to cache state. Each is the
  right answer for different data.
• Thundering herd: caches fail at the boundaries. TTL jitter prevents
  synchronized expirations; request coalescing prevents concurrent misses
  from stampeding the database. Production systems use both.
""")
        print(f"\n📊 Time spent per experiment:")
        for name, t in self.experiment_times.items():
            print(f"   {name}: {t:.1f}s")

        self.print_info("""
The next two case studies — Search Engine (Lessons 7-8) and AI-Enhanced
Search (Lessons 9-10) — depend heavily on the patterns you just felt.
Search engines cache popular queries with the same cache-aside pattern.
AI systems cache AI-generated answers because LLM calls are slow and
expensive. Same building blocks, same patterns, applied to new domains.

You're ready.
""")
        if os.path.exists(self.workspace):
            shutil.rmtree(self.workspace, ignore_errors=True)
            print(f"\n🧹 Cleaned up temporary workspace: {self.workspace}")

    # =======================================================================
    # Entry points
    # =======================================================================

    def run_full(self):
        try:
            self.run_welcome()
            self.experiment_1_db_bottleneck()
            self.experiment_2_cache_aside()
            self.experiment_3_invalidation()
            self.experiment_4_thundering_herd()
            self.show_summary()
        finally:
            if os.path.exists(self.workspace):
                shutil.rmtree(self.workspace, ignore_errors=True)

    def run_one(self, experiment_num: int):
        try:
            mapping = {
                1: self.experiment_1_db_bottleneck,
                2: self.experiment_2_cache_aside,
                3: self.experiment_3_invalidation,
                4: self.experiment_4_thundering_herd,
            }
            fn = mapping.get(experiment_num)
            if fn is None:
                print(f"Unknown experiment: {experiment_num}. Choose 1-4.")
                return
            print(f"\n  Running Experiment {experiment_num} directly...\n")
            fn()
        finally:
            if os.path.exists(self.workspace):
                shutil.rmtree(self.workspace, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description="Course 2 Lab 2: Service + Key-Value Store Discovery")
    parser.add_argument("experiment", nargs="?", type=int,
                        help="Optional experiment number (1-4) to run directly")
    parser.add_argument("--instant", action="store_true",
                        help="Disable typewriter effect (faster output)")
    args = parser.parse_args()

    lab = LabExperience()
    if args.instant:
        lab.instant_print = True

    if args.experiment is None:
        lab.run_full()
    else:
        lab.run_one(args.experiment)


if __name__ == "__main__":
    main()
