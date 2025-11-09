# ⚙️ FastAPI + MongoDB Template

Minimal, async-first backend template using **FastAPI**, **Motor (MongoDB)**, and a clean, modular layout.  
Includes scheduler (APScheduler), healthcheck, and a ready-to-extend auth router.

---

## 🚀 Quickstart

```bash
git clone <your-repo-url>
cd <repo>
python -m venv env && source env/bin/activate
pip install -r requirements.txt
cp sample.env .env
fastapi dev --host 127.0.0.1 --port 8000
````

Docs: [http://localhost:8000/docs][localhost]

---

## ⚙️ Environment

`.env` (override for production):

```env
ENV=dev
MONGO_URI=mongodb://localhost:27017
MONGO_DB=app
SECRET_KEY=change-me
CORS_ORIGINS=http://localhost:3000
```

`app/config.py` loads `app/docs/api_description.md` into the OpenAPI description.

---

## 📂 Structure

```
.
├── app
│   ├── database
│   │   ├── __init__.py
│   │   ├── motor.py
│   │   └── utils.py
│   ├── docs
│   │   └── api_description.md
│   ├── routers
│   │   ├── auth
│   │   │   └── endpoints.py
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
│   ├── auth.py
│   ├── config.py
│   ├── __init__.py
│   └── main.py
├── Dockerfile
├── LICENSE
├── README.md
├── requirements.txt
└── sample.env
```

---

## 🧩 Features

* Async MongoDB connection manager (Motor)
* Healthcheck router mounted at `/`
* Auth router skeleton under `routers/auth/`
* APScheduler integration with job registry
* Small DB utilities (`bulk_upsert`, timestamps)
* Centralized config, CORS, and security settings

---

## ▶️ Run with Docker

```bash
docker build -t fastapi-mongo-template .
docker run --env-file .env -p 8000:8000 fastapi-mongo-template
```

---

## ✅ Notes

* Python **3.12+**
* Production should set real `SECRET_KEY`, CORS origins, and a managed MongoDB
* OpenAPI description comes from `app/docs/api_description.md`

---

## 📜 License

[MIT © Awerito][license]

---

[localhost]: http://localhost:8000/docs
[license]: https://github.com/Awerito/fastapi-auth-template/blob/master/LICENSE
