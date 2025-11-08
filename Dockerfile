# Base
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
  && rm -rf /var/lib/apt/lists/*

# Builder
FROM base AS builder
WORKDIR /install
COPY requirements.txt .
RUN python -m venv /venv \
  && /venv/bin/pip install --upgrade pip \
  && /venv/bin/pip install -r requirements.txt

# Final
FROM base
ENV PATH="/venv/bin:$PATH"
WORKDIR /app
COPY --from=builder /venv /venv
COPY . /app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
