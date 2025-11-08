A clean, asynchronous API boilerplate built with [**FastAPI**][fastapi] and
[**Motor**][motor] (MongoDB async driver).  
Designed for scalability, modularity, and maintainability.

---

<details>
<summary>Click to expand</summary>
## 🌍 Design Philosophy

* **Minimal but realistic:** ready-to-extend structure with routing, DB, and
scheduler.
* **Async-first:** every operation is non-blocking — I/O, DB, background jobs.
* **Declarative main:** all startup/shutdown behavior is handled in the FastAPI
`lifespan`.
* **Consistent lifecycle:** one entrypoint, one scheduler, one DB connection
manager.
* **Readable architecture:** each feature lives in its own module.

---

## 🧩 Project Structure

```
.
├── app
│   ├── database
│   │   ├── __init__.py
│   │   ├── motor.py
│   │   └── utils.py
│   ├── routers
│   │   └── healthcheck
│   │       └── endpoints.py
│   ├── scheduler
│   │   ├── jobs
│   │   │   ├── example.py
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── jobs.py
│   │   └── motor.py
│   ├── utils
│   │   └── logger.py
│   ├── config.py
│   ├── __init__.py
│   ├── main.py
│   └── docs
│       └── api_description.md
├── Dockerfile
├── LICENSE
├── README.md
├── requirements.txt
└── sample.env
```

Each domain (database, scheduler, router, utils) is isolated, promoting
testability and modular scaling.

---

## ⚙️ Application Lifecycle

The app manages its entire lifecycle through FastAPI’s `lifespan` context:

* Opens the MongoDB connection pool.
* Starts the scheduler (background jobs).
* Gracefully stops all resources on shutdown.

This keeps `main.py` declarative — only includes routers and lifecycle hooks.

---

## 💓 Healthcheck Endpoint

**Purpose:** a minimal root endpoint used for readiness/liveness probes.

```python
GET /
→ 200 OK
{
  "status": "ok",
  "name": "API Template",
  "version": "0.1.0",
  "env": "development"
}
```

* Mounted in `app/routers/healthcheck/endpoints.py`.
* Registered in `main.py` via `app.include_router(...)`.
* Appears under the “Healthcheck” tag in `/docs`.

---

## ⏱ Scheduler Integration (APScheduler)

**Purpose:** to schedule async background jobs at fixed intervals or cron
expressions.

### Design

* Defined in `app/scheduler/motor.py`, started on app startup.
* Jobs are registered dynamically via `register_jobs` in
`app/scheduler/jobs.py`.
* Each job lives in its own file under `app/scheduler/jobs/`.

### Example behavior

* When `ENV` starts with `"dev"`, runs a test job every 5 minutes.
* On startup:

  ```
  [INFO] Scheduler started successfully
  Example job executed
  ```

### Example Job Philosophy

* Keep jobs stateless and idempotent.
* Write to MongoDB using the async client from the shared connection.
* Log outputs instead of printing to stdout.
* Use UTC internally; localize only when displaying results.

---

## 🧭 Database Layer Philosophy

* **Connection handling:** done through a context-managed
`MongoDBConnectionManager`.
* **Asynchronous:** all reads and writes use Motor (async I/O).
* **Write safety:** `bulk_upsert` is the main pattern for inserts/updates.
* **Deterministic keys:** each collection defines its own logical key (e.g.,
`email`, `(monitor_id, ts)`).

---

## 🧱 Database Utilities — Usage Examples

These examples illustrate how to use the built-in helpers in
`app/database/utils.py` for efficient, idempotent bulk operations.

### 1️⃣ Simple upsert by key

```python
from app.database.utils import bulk_upsert
from datetime import datetime, timezone

rows = [
    {"email": "a@x.com", "name": "A"},
    {"email": "b@x.com", "name": "B"},
]

res = await bulk_upsert(
    db,
    collection="users",
    rows=rows,
    key_fields=["email"],
    set_on_insert={"created_at": datetime.now(timezone.utc)},
)
# → {'matched': 2, 'modified': 0, 'upserted': 0}
```

---

### 2️⃣ Composite key upsert

```python
metrics = [
    {"monitor_id": 1388, "ts": 1731052800, "oxygen": 7.2},
    {"monitor_id": 1388, "ts": 1731056400, "oxygen": 7.0},
]

res = await bulk_upsert(
    db,
    collection="monitor_metrics",
    rows=metrics,
    key_fields=["monitor_id", "ts"],
    set_on_insert={"created_at": datetime.now(timezone.utc)},
)
```

---

### 3️⃣ Custom key function

```python
def normalize_email_key(doc: dict) -> dict:
    e = doc.get("email")
    if not e:
        raise ValueError("Missing key field 'email'")
    return {"email": e.strip().lower()}

await bulk_upsert(
    db,
    collection="users",
    rows=[{"email": "  A@X.com  ", "name": "A"}],
    key_func=normalize_email_key,
)
```

---

### 4️⃣ Empty batch (no-op)

```python
await bulk_upsert(db, collection="users", rows=[], key_fields=["email"])
# → {'matched': 0, 'modified': 0, 'upserted': 0}
```

---

### 5️⃣ Key validation errors

```python
rows = [{"email": None, "name": "A"}]
await bulk_upsert(db, collection="users", rows=rows, key_fields=["email"])
# Raises ValueError("Null key field 'email' in document")
```

---

### 6️⃣ `_id` safely ignored

```python
rows = [{"_id": "ignored", "email": "a@x.com", "name": "A"}]
await bulk_upsert(db, collection="users", rows=rows, key_fields=["email"])
```

The helper strips `_id` before writing to avoid conflicts with
MongoDB-generated IDs.

---

## ✅ Patterns and Guidelines

* Each collection should define clear `key_fields`.
* Use `set_on_insert` for immutable attributes (e.g. `created_at`, `source`).
* Avoid mutation logic inside `key_func`; only normalization/validation.
* Prefer smaller batches with frequent writes.
* Always log the return of `bulk_upsert` for job traceability.

---

## 🧰 Core Dependencies

| Package                                              | Purpose                    |
| ---------------------------------------------------- | -------------------------- |
| [fastapi][fastapi]                                   | Main async API framework   |
| [motor][motor]                                       | Async MongoDB driver       |
| [pydantic][pydantic]                                 | Data validation and typing |
| [apscheduler](https://pypi.org/project/APScheduler/) | Background task scheduling |
| [uvicorn][uvicorn]                                   | ASGI server for dev/prod   |

---

## 🧱 Setup and Execution

```bash
pip install -r requirements.txt
cp sample.env .env
uvicorn app.main:app --reload
```

Access:

* `/` → Healthcheck
* `/docs` → Interactive API documentation

---

## 🧾 License

Released under the **MIT License**.
Free to use, extend, and redistribute.
</details>

[fastapi]: https://fastapi.tiangolo.com/
[motor]: https://motor.readthedocs.io/
[pydantic]: https://docs.pydantic.dev/latest/
[uvicorn]: https://www.uvicorn.org/
[oid]: https://www.mongodb.com/docs/manual/reference/bson-types/#objectid
[rest]: https://developer.mozilla.org/en-US/docs/Glossary/REST
[http]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods
[json]: https://www.json.org/json-en.html
[iso8601]: https://en.wikipedia.org/wiki/ISO_8601
[status]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
