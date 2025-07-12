# Fastapi Template

## Setup

Configure `sample.env` and rename it to `.env`.

- Local:

```sh
$ python -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
$ fastapi dev main.py
```

- Docker compose:

```sh
docker-compose up -d
```

## Caprover

Use the Webhook to deploy.

## Roles and Scopes

This template supports OAuth2 scopes and role management. Roles are groups of
scopes that can be assigned to users. An initial `admin` role is created on the
first start and the default `admin` user is assigned to it.

New roles can be managed through the `/role/` endpoints and users can have roles
assigned through the regular user CRUD endpoints.
