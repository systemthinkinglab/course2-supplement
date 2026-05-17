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
Lesson 3: Service + File Store Media Handling Discovery Lab
Interactive Python Application

This application guides students through four progressive experiments that
build deep intuition for handling user-uploaded media. Same work, different
storage choice — and you'll feel why the choice matters.
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
    from building_blocks import Service, Worker, FileStore, RelationalDB, KeyValueStore, Queue
except ImportError:
    try:
        # Package import — works when building_blocks/ is a top-level package
        from building_blocks.building_blocks import Service, Worker, FileStore, RelationalDB, KeyValueStore, Queue
    except ImportError:
        print("Error: Could not import building_blocks module.")
        print("Expected building_blocks.py next to this file, OR building_blocks/ package at repo root.")
        sys.exit(1)


class LabExperience:
    """Interactive lab experience for Lesson 3: Service + File Store"""

    def __init__(self, student_name: str = "Student"):
        self.student_name = student_name
        self.experiment_times = {}

        self.separator = "=" * 80
        self.mini_separator = "-" * 40

        self.typewriter_speed = 0.03
        self.fast_typewriter_speed = 0.01
        self.instant_print = False

        self.print_lock = threading.Lock()

        # Use a temp dir for File Store so the lab never pollutes the user's repo
        self.workspace = tempfile.mkdtemp(prefix="lab1_filestore_")

    # -----------------------------------------------------------------------
    # Print helpers (typewriter, thread-safe direct, headers)
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

    def print_action(self, text: str):
        self.typewriter_print(f"⚡ {text}", speed=self.fast_typewriter_speed)

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
                choice_input = input(f"\n❓ Enter your choice (1-{len(choices)}): ").strip()
                choice_num = int(choice_input)
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
    # Shared helpers for media work
    # -----------------------------------------------------------------------

    def generate_fake_image(self, size_kb: int) -> bytes:
        """Generate a deterministic-ish bytes payload of the requested KB size."""
        return bytes(random.getrandbits(8) for _ in range(size_kb * 1024))

    def fake_metadata(self, photo_num: int) -> dict:
        """Build a small metadata dict for one photo."""
        topics = ["sunset", "mountain", "city", "ocean", "portrait", "macro", "street"]
        return {
            "filename": f"photo_{photo_num:04d}.jpg",
            "topic": random.choice(topics),
            "uploaded_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    # -----------------------------------------------------------------------
    # Welcome
    # -----------------------------------------------------------------------

    def run_welcome(self):
        self.print_header("WELCOME TO SYSTEMS THINKING IN THE AI ERA")
        print("\n🎓 Systems Thinking in the AI Era II: Content & Information Systems")
        print("📚 Lesson 3: Service + File Store Media Handling Discovery Lab\n")

        self.typewriter_print("Transform from a code writer who stuffs binaries into databases")
        self.typewriter_print("to a system thinker who knows exactly where bytes belong.")

        self.student_name = input("\n\n👤 What's your name? ").strip() or "Student"
        self.typewriter_print(f"\nWelcome, {self.student_name}! Let's discover the pattern together.")

        self.print_info("""
You're about to feel — not just read about — why every serious content
platform separates binary files from structured metadata.

You'll run four experiments:
1. Naive Storage: Photos as BLOBs in a Relational Database (the pain)
2. Service + File Store: Bytes in File Store, metadata in DB (the relief)
3. Media Processing Pipeline: Queue + Worker for async thumbnail generation
4. CDN Integration: Edge caching for global delivery

After each experiment you'll answer three reflection questions with
immediate educational feedback.
""")
        self.wait_for_enter("Ready to discover? Press ENTER to begin!")

    # =======================================================================
    # EXPERIMENT 1 — Naive: photos as BLOBs in a Relational Database
    # =======================================================================

    def experiment_1_naive_blob_in_db(self):
        self.print_experiment("1 - NAIVE STORAGE (PHOTOS AS BLOBS IN THE DATABASE)")

        self.print_info("""
In this experiment, you'll store the actual JPEG bytes inside a Relational
Database column. This is what many beginners try first — "I already have a
database, why add another storage system?"

You'll upload progressively more photos, then run a simple metadata query
("show me all filenames"). Watch what happens to query time as the
database fills with binary data.
""")
        self.wait_for_enter()

        db = RelationalDB("naive_photos_db", db_path=os.path.join(self.workspace, "naive.db"))
        db.create_table(
            "photos",
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "filename TEXT, topic TEXT, uploaded_at TEXT, image_blob BLOB"
        )

        self.typewriter_print("\n🚀 Uploading photos directly into the database column...\n")
        upload_batches = [(10, 200), (50, 200), (200, 200)]  # (count, KB per photo)

        metadata_query_times = []
        start_time = time.time()

        for batch_idx, (count, kb) in enumerate(upload_batches, 1):
            batch_start = time.time()
            for i in range(count):
                meta = self.fake_metadata(i)
                blob = self.generate_fake_image(kb)
                db.insert("photos", {
                    "filename": meta["filename"],
                    "topic": meta["topic"],
                    "uploaded_at": meta["uploaded_at"],
                    "image_blob": blob,
                })
            insert_time = time.time() - batch_start

            # Now run a pure-metadata query and time it
            query_start = time.time()
            rows = db.select("photos", where_clause="topic = ?", params=["sunset"])
            query_time = time.time() - query_start
            metadata_query_times.append(query_time)

            db_size_bytes = os.path.getsize(os.path.join(self.workspace, "naive.db"))
            self.typewriter_print(
                f"📦 Batch {batch_idx}: inserted {count} photos × {kb}KB "
                f"in {insert_time:.2f}s",
                speed=self.fast_typewriter_speed,
            )
            self.typewriter_print(
                f"   Metadata query (\"sunset photos\"): {query_time*1000:.1f}ms "
                f"on {len(rows)} matching rows",
                speed=self.fast_typewriter_speed,
            )
            self.typewriter_print(
                f"   Database file size: {db_size_bytes / (1024 * 1024):.1f} MB",
                speed=self.fast_typewriter_speed,
            )
            print()

        total_time = time.time() - start_time
        self.experiment_times['experiment_1'] = total_time

        print(f"📊 Naive Storage Statistics:")
        print(f"   🗄️  Final DB size: "
              f"{os.path.getsize(os.path.join(self.workspace, 'naive.db')) / (1024*1024):.1f} MB")
        print(f"   ⏱️  Metadata query time progression (ms): "
              f"{[round(t*1000, 1) for t in metadata_query_times]}")
        print(f"   📈 Query slowed by "
              f"{(metadata_query_times[-1] / metadata_query_times[0]):.1f}x "
              f"between batch 1 and batch 3")

        self.print_warning(
            "The database had to wade through MB of binary data just to answer a "
            "metadata question. That's the problem."
        )

        self.print_header("EXPERIMENT 1 REFLECTIONS", style="sub")

        self.ask_multiple_choice(
            "Why did the metadata query get slower as you added more photos?",
            [
                "Because the database had to scan past binary BLOB data to read the metadata columns",
                "Because SQLite is too slow for any kind of query",
                "Because the photo count grew, and that always slows queries linearly",
            ],
            [
                "Exactly right. Even when you only SELECT metadata columns, the row layout means the database engine still walks past the BLOBs. Big rows hurt every read on the table, even reads that don't touch the binary data.",
                "Not quite. SQLite is plenty fast for metadata-only queries on millions of rows. The slowdown here is caused specifically by mixing big binaries with small metadata in the same row.",
                "Row count isn't the culprit. The same 260 rows would be fast with a small index. The slowdown comes from the binary payload bloating the rows, slowing every page read.",
            ],
        )

        self.ask_multiple_choice(
            "What else suffers when you store photos as BLOBs in the database?",
            [
                "Backups, replication, and any operation that reads the full table",
                "Only the photo download path, since the binary data is the bottleneck",
                "Nothing else — the metadata query was just an unlucky outlier",
            ],
            [
                "Yes — and this is the real production cost. Backups balloon. Replication lags. Even VACUUM takes forever. A 200MB photo column quietly imposes itself on every operation that touches the table.",
                "Download is one impact, but the bigger surprise is how much non-download work gets slower. Backups, replication, and index maintenance all degrade because the rows themselves are huge.",
                "Other operations definitely suffer too. The metadata query was the most visible symptom, but backup time, replication lag, and dump/restore all degrade with BLOBs in rows.",
            ],
        )

        self.ask_multiple_choice(
            "What would a senior engineer do differently?",
            [
                "Move the binary photo data out of the database entirely; keep only metadata in rows",
                "Add more indexes to the database to compensate",
                "Switch to a NoSQL database — it would handle the BLOBs better",
            ],
            [
                "Yes — this is the canonical pattern. Database holds metadata; File Store holds the bytes. Each block does what it's good at. You'll feel the relief in Experiment 2.",
                "Indexes can speed up specific lookups, but they can't fix the fundamental problem of bloated rows. The architecture itself is the issue. The fix is to separate concerns, not patch over the symptom.",
                "Different database technology won't help here. Document stores have the same problem with large binary fields. The fix is architectural — get the bytes out of the database entirely and put them in a File Store.",
            ],
        )

        if self.ask_yes_no("Ready to feel the relief of separating bytes from metadata?"):
            self.experiment_2_service_plus_filestore()

    # =======================================================================
    # EXPERIMENT 2 — Service + File Store split
    # =======================================================================

    def experiment_2_service_plus_filestore(self):
        self.print_experiment("2 - SERVICE + FILE STORE (BYTES OUT OF THE DATABASE)")

        self.print_info("""
Now you'll do it right. The Service receives the upload, writes the raw
bytes into a File Store, and writes only the metadata + a file_id reference
into the Relational Database.

You'll upload the same volume of photos. Watch how the metadata query
time stays flat regardless of how many photos exist. The database stays
lean because it never has to hold a single byte of image data.
""")
        self.wait_for_enter()

        db = RelationalDB("split_photos_db", db_path=os.path.join(self.workspace, "split.db"))
        db.create_table(
            "photos",
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "filename TEXT, topic TEXT, uploaded_at TEXT, file_id TEXT"
        )
        file_store = FileStore("photo_blobs", base_path=os.path.join(self.workspace, "filestore_split"))

        upload_service = Service("upload_service")

        @upload_service.route("/upload")
        def upload_handler(data):
            file_id = f"photo_{int(time.time()*1000000)}_{random.randint(1000,9999)}"
            file_store.store_file(file_id, data["content"])
            db.insert("photos", {
                "filename": data["filename"],
                "topic": data["topic"],
                "uploaded_at": data["uploaded_at"],
                "file_id": file_id,
            })
            return {"status": "stored", "file_id": file_id}

        self.typewriter_print("\n🚀 Uploading through Service → File Store + Relational DB...\n")
        upload_batches = [(10, 200), (50, 200), (200, 200)]
        metadata_query_times = []
        start_time = time.time()

        for batch_idx, (count, kb) in enumerate(upload_batches, 1):
            batch_start = time.time()
            for i in range(count):
                meta = self.fake_metadata(i)
                blob = self.generate_fake_image(kb)
                upload_service.handle_request("/upload", data={
                    "filename": meta["filename"],
                    "topic": meta["topic"],
                    "uploaded_at": meta["uploaded_at"],
                    "content": blob,
                })
            insert_time = time.time() - batch_start

            query_start = time.time()
            rows = db.select("photos", where_clause="topic = ?", params=["sunset"])
            query_time = time.time() - query_start
            metadata_query_times.append(query_time)

            db_size_bytes = os.path.getsize(os.path.join(self.workspace, "split.db"))
            self.typewriter_print(
                f"📦 Batch {batch_idx}: inserted {count} photos × {kb}KB "
                f"in {insert_time:.2f}s",
                speed=self.fast_typewriter_speed,
            )
            self.typewriter_print(
                f"   Metadata query (\"sunset photos\"): {query_time*1000:.1f}ms "
                f"on {len(rows)} matching rows",
                speed=self.fast_typewriter_speed,
            )
            self.typewriter_print(
                f"   DB size: {db_size_bytes / 1024:.1f} KB   "
                f"File Store size: "
                f"{file_store.get_stats()['total_size_mb']:.1f} MB",
                speed=self.fast_typewriter_speed,
            )
            print()

        total_time = time.time() - start_time
        self.experiment_times['experiment_2'] = total_time

        print(f"📊 Split Storage Statistics:")
        print(f"   🗄️  Final DB size: "
              f"{os.path.getsize(os.path.join(self.workspace, 'split.db'))/1024:.1f} KB")
        print(f"   🗂️  File Store size: "
              f"{file_store.get_stats()['total_size_mb']:.1f} MB")
        print(f"   ⏱️  Metadata query time progression (ms): "
              f"{[round(t*1000, 1) for t in metadata_query_times]}")
        print(f"   📉 Metadata query stayed flat — the DB doesn't carry the binary weight")

        self.print_result("Database stayed lean. File Store absorbed the bytes. Queries are flat.")

        self.print_header("EXPERIMENT 2 REFLECTIONS", style="sub")

        self.ask_multiple_choice(
            "Why did metadata queries stay fast in Experiment 2?",
            [
                "Because the database rows are tiny — only metadata + a reference, never the bytes",
                "Because we used a different database engine than Experiment 1",
                "Because the photo bytes happened to fit in memory this time",
            ],
            [
                "Exactly. The Relational Database row is now just `filename + topic + uploaded_at + file_id` — a few hundred bytes. Page reads are fast because each page holds many rows. File Store carries the binary weight separately.",
                "Same SQLite engine in both experiments. The win is purely architectural — keeping bytes out of the database rows.",
                "Memory isn't the variable here. Even with the bytes on disk in both cases, the speedup comes from making the database rows themselves small. The File Store absorbs the binary weight.",
            ],
        )

        self.ask_multiple_choice(
            "What is the role of the `file_id` column in the metadata table?",
            [
                "A pointer — it tells the application where to fetch the binary content from the File Store when needed",
                "An optimization for full-text search across photo content",
                "A backup copy of the photo's bytes in case the File Store fails",
            ],
            [
                "Correct. `file_id` is the bridge between the structured world (database) and the binary world (File Store). When you need the image, you look up the metadata row, then use the file_id to fetch from the File Store.",
                "Not the role here. The file_id is a storage pointer, not a search index. Photo content isn't indexed for text search in this pattern — that would be a separate concern.",
                "No — the file_id is a reference, not a copy. The bytes live in the File Store. If the File Store fails, the file_id alone won't recover the data — that's what backups and File Store redundancy are for.",
            ],
        )

        self.ask_multiple_choice(
            "Which real-world systems use this exact pattern?",
            [
                "Instagram, Dropbox, YouTube, and nearly every platform that handles user uploads",
                "Only enterprise systems with strict compliance requirements",
                "Mostly read-heavy systems like blogs, not write-heavy systems like photo platforms",
            ],
            [
                "Right. This split — metadata in a database, blobs in object storage like S3 — is the universal pattern for user-generated content. The block names change (S3, GCS, R2) but the architectural shape is identical.",
                "It's much more common than that. Every social media platform, every file-sharing service, every backup system uses this split. It's the default pattern for any system that handles user-uploaded binaries.",
                "Actually it's most critical for write-heavy systems. The more uploads you handle, the more painful it becomes to keep binaries in the database. The pattern scales beautifully for both reads and writes.",
            ],
        )

        if self.ask_yes_no("Ready to add async processing with Queue + Worker?"):
            self.experiment_3_processing_pipeline()

    # =======================================================================
    # EXPERIMENT 3 — Media processing pipeline (Queue + Worker)
    # =======================================================================

    def experiment_3_processing_pipeline(self):
        self.print_experiment("3 - MEDIA PROCESSING PIPELINE (QUEUE + WORKER)")

        self.print_info("""
A real upload doesn't just store the original — it generates thumbnails,
resizes for mobile, maybe runs content moderation. All of that takes
seconds per photo, and you cannot make the user wait.

In this experiment, the upload Service hands the user back an instant
acknowledgment, drops a job on a Queue, and a Worker generates the
thumbnail in the background. You'll see the user's upload return
immediately while the thumbnail appears moments later.
""")
        self.wait_for_enter()

        file_store = FileStore("media_pipeline_store",
                               base_path=os.path.join(self.workspace, "filestore_pipeline"))
        db = RelationalDB("pipeline_db", db_path=os.path.join(self.workspace, "pipeline.db"))
        db.create_table(
            "photos",
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "filename TEXT, original_file_id TEXT, thumbnail_file_id TEXT, status TEXT"
        )

        task_queue = Queue("thumbnail_queue")
        worker = Worker("thumbnail_worker")

        def generate_thumbnail_work(data: dict) -> dict:
            """The thumbnail generation work — same function whether sync or async."""
            time.sleep(2)  # simulate image resize
            original_bytes = file_store.retrieve_file(data["original_file_id"])
            thumbnail_bytes = original_bytes[: len(original_bytes) // 10]  # mock shrink
            thumb_id = f"thumb_{data['original_file_id']}"
            file_store.store_file(thumb_id, thumbnail_bytes)
            db.update("photos",
                      {"thumbnail_file_id": thumb_id, "status": "thumbnailed"},
                      where_clause="id = ?", params=[data["photo_id"]])
            return {"thumb_id": thumb_id}

        worker.register_job_type("generate_thumbnail", generate_thumbnail_work)

        @task_queue.subscriber("generate_thumbnail")
        def dispatch_thumbnail(message):
            self.direct_print(
                f"   📬 Queue → Worker: generate thumbnail for photo "
                f"id={message['photo_id']}"
            )
            worker.submit_job("generate_thumbnail", message)
            return {"status": "queued"}

        worker.start()

        upload_service = Service("media_upload_service")

        @upload_service.route("/upload")
        def upload_handler(data):
            # Step 1: write the original to File Store
            file_id = f"orig_{int(time.time()*1000000)}_{random.randint(1000,9999)}"
            file_store.store_file(file_id, data["content"])

            # Step 2: write metadata row (status = pending until thumbnail ready)
            photo_id = db.insert("photos", {
                "filename": data["filename"],
                "original_file_id": file_id,
                "thumbnail_file_id": None,
                "status": "pending",
            })

            # Step 3: enqueue thumbnail job — DO NOT WAIT
            task_queue.enqueue(
                {"photo_id": photo_id, "original_file_id": file_id},
                message_type="generate_thumbnail",
            )

            return {"status": "received", "photo_id": photo_id}

        self.typewriter_print("\n🚀 Uploading 5 photos through the async pipeline...\n")
        upload_times = []
        start_time = time.time()

        for i in range(5):
            blob = self.generate_fake_image(1024)  # 1 MB photo
            t0 = time.time()
            response = upload_service.handle_request("/upload", data={
                "filename": f"travel_{i:03d}.jpg",
                "content": blob,
            })
            t_upload = time.time() - t0
            upload_times.append(t_upload)
            self.typewriter_print(
                f"📤 Upload #{i+1} acknowledged in {t_upload*1000:.0f}ms "
                f"(photo_id={response['data']['photo_id']})",
                speed=self.fast_typewriter_speed,
            )

        self.typewriter_print(
            f"\n⚡ User experience: all 5 uploads acknowledged in "
            f"{sum(upload_times)*1000:.0f}ms total. "
            f"Thumbnails are still being generated in the background."
        )

        # Wait for background work to drain
        self.print_info("\n⏳ Waiting for the Worker to finish generating thumbnails...")
        max_wait = 30
        elapsed = 0
        while elapsed < max_wait:
            stats = worker.get_stats()
            done = stats['completed_jobs'] + stats['failed_jobs']
            self.direct_print(f"   📊 Worker progress: {done}/5 thumbnails generated")
            if done >= 5:
                break
            time.sleep(2)
            elapsed += 2

        total_time = time.time() - start_time
        self.experiment_times['experiment_3'] = total_time

        # Show how many DB rows now have thumbnails
        thumbnailed = db.select("photos", where_clause="status = ?", params=["thumbnailed"])
        print(f"\n📊 Pipeline Statistics:")
        print(f"   ⚡ Average upload acknowledgment: "
              f"{(sum(upload_times)/len(upload_times))*1000:.0f}ms")
        print(f"   🖼️  Photos with thumbnails: {len(thumbnailed)}/5")
        print(f"   🧵 Worker job stats: {worker.get_stats()}")

        worker.stop()
        task_queue.stop()

        self.print_result(
            "User got instant acknowledgment. Thumbnails generated in the background. "
            "This is how Instagram, Flickr, and every modern photo platform works."
        )

        self.print_header("EXPERIMENT 3 REFLECTIONS", style="sub")

        self.ask_multiple_choice(
            "What problem does the Queue solve in this pipeline?",
            [
                "It decouples the user's upload request from the slow thumbnail work",
                "It makes thumbnail generation faster",
                "It stores the photos so the File Store doesn't have to",
            ],
            [
                "Exactly. The Queue accepts the job instantly so the user gets an acknowledgment in milliseconds. The Worker drains the Queue at its own pace. Upload speed is decoupled from processing speed — that's the architectural win.",
                "Thumbnail generation takes the same time whether queued or not. The Queue doesn't speed up the work — it lets the user not have to wait for it.",
                "The Queue is a coordination block, not a storage block. The File Store still holds the actual photos. The Queue only holds short job descriptions ('generate thumbnail for photo X'), not the binary content.",
            ],
        )

        self.ask_multiple_choice(
            "Why is the photo metadata row marked status='pending' initially, then updated to 'thumbnailed'?",
            [
                "So the UI can show 'processing' until the thumbnail is ready, then refresh to show it",
                "Because the database can only insert one column at a time",
                "It's not necessary — the Worker could just create the row directly",
            ],
            [
                "Right. The pending → thumbnailed state machine lets the front-end show 'still processing' immediately and 'ready' after a poll or a push notification. Async processing always implies status tracking in the metadata.",
                "Databases can insert all columns at once. The two-step pattern is intentional — the row exists from the moment of upload so the user can see their photo right away, even before the thumbnail is generated.",
                "It is necessary. If the Worker created the row, the user wouldn't have a photo_id to reference until the Worker finished — which defeats the purpose of immediate acknowledgment. The Service must create the row first so the user can reference the photo before processing completes.",
            ],
        )

        self.ask_multiple_choice(
            "How would you scale this pipeline if uploads spiked 10x?",
            [
                "Add more Workers reading from the same Queue — they share the load automatically",
                "Make the Service handle uploads synchronously to slow down submissions",
                "Resize photos client-side and skip the Worker entirely",
            ],
            [
                "Right — and this is the elasticity benefit of the Queue + Worker pattern. The Queue absorbs the spike; more Workers drain it faster. You don't need to change the upload path or the database — just add Workers.",
                "Slowing the Service down would make the user experience worse, not better. The whole point of the async pipeline is that uploads stay fast no matter what's happening downstream. The Queue is the shock absorber.",
                "Client-side processing works for some cases (you'll see it in Photo Gallery), but for high-volume multi-user platforms you generally want server-side control. Client-side processing is great for single-author tools, not multi-tenant uploads.",
            ],
        )

        if self.ask_yes_no("Ready to add a CDN for global delivery?"):
            self.experiment_4_cdn()

    # =======================================================================
    # EXPERIMENT 4 — CDN integration
    # =======================================================================

    def experiment_4_cdn(self):
        self.print_experiment("4 - CDN INTEGRATION (EDGE CACHING FOR GLOBAL DELIVERY)")

        self.print_info("""
The File Store lives in one region. A reader in Tokyo requesting an image
from a US-East File Store pays a 200ms round-trip — every time.

A CDN sits in front of the File Store with edge servers worldwide. The
first request from a region pulls from the origin and caches at the edge.
Subsequent requests from the same region are served from the local edge
in 20ms instead of 200ms.

You'll simulate readers in three regions and watch how cache hits transform
delivery latency. The CDN itself is a Service + Key-Value Store under the
hood — same pattern you already know.
""")
        self.wait_for_enter()

        file_store = FileStore("cdn_origin",
                               base_path=os.path.join(self.workspace, "filestore_cdn"))

        # Seed the File Store with a few popular photos
        photo_ids = []
        for i in range(5):
            blob = self.generate_fake_image(500)
            file_store.store_file(f"popular_{i}", blob)
            photo_ids.append(f"popular_{i}")

        # CDN simulation: an edge cache per region, all backed by KV stores
        edge_caches = {
            region: KeyValueStore(f"edge_{region}", max_size=100)
            for region in ["us-east", "europe", "tokyo"]
        }

        # Simulated network latency from each region to origin
        origin_latency = {"us-east": 0.02, "europe": 0.12, "tokyo": 0.2}
        edge_latency = 0.02  # uniform — readers always reach their nearest edge fast

        def fetch_via_cdn(region: str, file_id: str) -> float:
            """Return the wall-clock latency for one fetch via the regional CDN."""
            edge = edge_caches[region]
            t0 = time.time()
            cached = edge.get(file_id)
            if cached is not None:
                time.sleep(edge_latency)  # edge hit
                return time.time() - t0

            # cache miss — pull from origin, populate edge
            time.sleep(origin_latency[region])
            content = file_store.retrieve_file(file_id)
            edge.set(file_id, content, ttl_seconds=300)
            return time.time() - t0

        # Workload: 30 reads per region, half on the same hot photo, half random
        regions = list(edge_caches.keys())
        per_region = 30
        results = {region: {"latencies": [], "hits": 0, "misses": 0} for region in regions}

        self.typewriter_print("\n🚀 Simulating reader traffic from three regions...\n")
        for region in regions:
            for i in range(per_region):
                # 60% of reads target the same hot photo, 40% are random
                if random.random() < 0.6:
                    file_id = "popular_0"
                else:
                    file_id = random.choice(photo_ids)

                was_hit = edge_caches[region].get(file_id) is not None
                latency = fetch_via_cdn(region, file_id)
                results[region]["latencies"].append(latency)
                if was_hit:
                    results[region]["hits"] += 1
                else:
                    results[region]["misses"] += 1

        # Report
        print()
        for region in regions:
            r = results[region]
            avg_ms = (sum(r["latencies"]) / len(r["latencies"])) * 1000
            hit_rate = r["hits"] / per_region
            self.typewriter_print(
                f"📍 {region:>8}: {per_region} reads, "
                f"hit rate {hit_rate*100:.0f}%, "
                f"avg latency {avg_ms:.0f}ms "
                f"(origin RTT for region: {origin_latency[region]*1000:.0f}ms)",
                speed=self.fast_typewriter_speed,
            )

        self.experiment_times['experiment_4'] = sum(
            sum(r["latencies"]) for r in results.values()
        )

        self.print_result(
            "Edge caching turned a 200ms Tokyo round-trip into a 20ms edge hit "
            "for the majority of reads."
        )

        self.print_header("EXPERIMENT 4 REFLECTIONS", style="sub")

        self.ask_multiple_choice(
            "Why is the average latency for Tokyo dramatically lower than the origin round-trip?",
            [
                "Because most reads are hitting the local Tokyo edge cache, not the US origin",
                "Because Tokyo had a faster internet connection in this simulation",
                "Because the File Store moved closer to Tokyo during the test",
            ],
            [
                "Exactly. After the first miss, popular content lives at the edge. Subsequent reads are answered locally. The geographic distance to origin only matters for cache misses — and a well-tuned CDN keeps the miss rate low.",
                "Network speed was constant. The improvement came entirely from cache hits at the local edge. CDN architecture is about geography, not bandwidth.",
                "The File Store stayed in one place. What changed is that the popular files are now also cached at the Tokyo edge. Origin distance still matters on misses, but hits never touch the origin.",
            ],
        )

        self.ask_multiple_choice(
            "What building blocks does a CDN compose at the architectural level?",
            [
                "Service (request handling) + Key-Value Store (edge cache) + File Store (origin)",
                "A brand-new building block called 'CDN' that doesn't decompose further",
                "Worker + Queue (CDNs are just async pipelines)",
            ],
            [
                "Right. There is no 'CDN' primitive — it's a familiar composition you've already seen. Service in front of a Key-Value Store cache, with a File Store as the authoritative origin. Same pattern as Jasmine's Media Cache, scaled geographically.",
                "CDNs decompose cleanly into building blocks you already know. Naming them as a black box hides the fact that you can reason about them with your existing vocabulary.",
                "CDNs are read-path infrastructure, not async pipelines. Workers come into play for cache invalidation or pre-warming, but the core read path is Service + Key-Value Store + File Store.",
            ],
        )

        self.ask_multiple_choice(
            "When does adding a CDN NOT help?",
            [
                "When content is unique per user (every read is a cache miss) or when traffic is purely local",
                "When you have more than a million users globally",
                "When the File Store is fast — CDN only helps slow storage",
            ],
            [
                "Right. CDNs win when the same content is requested by many readers across regions. Per-user dynamic content (like a personalized feed) can't be cached at the edge in the same way. And if all your readers are next door to your origin, the CDN adds a hop for no latency benefit.",
                "Scale alone doesn't determine CDN value — content-sharing patterns do. A million users all asking for different personalized pages won't benefit; ten thousand users all asking for the same trending article absolutely will.",
                "File Store speed isn't the bottleneck the CDN solves — geographic distance is. Even with the fastest origin storage, a Tokyo reader still pays a long network round-trip. The CDN moves the content closer geographically.",
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
You've now experienced — not just read about — the canonical pattern for
handling media in any content system.

What you discovered:

• Naive: photos in DB rows bloat the table and slow every read on it.
• Right: bytes go in File Store, metadata + file_id go in the Relational
  Database. Each block does what it's best at.
• Pipeline: Queue + Worker decouple slow processing from the upload path.
  Users get instant acknowledgments while Workers do the heavy lifting.
• Global: a CDN is just Service + KV cache + File Store origin, composed
  geographically. Same pattern you already know, applied at the edge.
""")

        print(f"\n📊 Time spent per experiment:")
        for name, t in self.experiment_times.items():
            print(f"   {name}: {t:.1f}s")

        self.print_info("""
The next two case studies — Video Streaming and Photo Gallery — both
build on this pattern. Video adds Workers for transcoding and chunking
on top of File Store. Photo Gallery shows that for single-author systems,
you can even skip server-side processing entirely. Same building blocks,
different shapes, depending on requirements.

You are now ready to read those case studies with the pattern already
embedded in your hands.
""")

        # Clean up the workspace
        if os.path.exists(self.workspace):
            shutil.rmtree(self.workspace, ignore_errors=True)
            print(f"\n🧹 Cleaned up temporary workspace: {self.workspace}")

    # =======================================================================
    # Entry points
    # =======================================================================

    def run_full(self):
        try:
            self.run_welcome()
            self.experiment_1_naive_blob_in_db()
            self.experiment_2_service_plus_filestore()
            self.experiment_3_processing_pipeline()
            self.experiment_4_cdn()
            self.show_summary()
        finally:
            if os.path.exists(self.workspace):
                shutil.rmtree(self.workspace, ignore_errors=True)

    def run_one(self, experiment_num: int):
        try:
            mapping = {
                1: self.experiment_1_naive_blob_in_db,
                2: self.experiment_2_service_plus_filestore,
                3: self.experiment_3_processing_pipeline,
                4: self.experiment_4_cdn,
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
    parser = argparse.ArgumentParser(description="Course 2 Lab 1: Service + File Store Discovery")
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
