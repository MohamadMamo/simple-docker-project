# simple-docker-project

A small Flask + PostgreSQL API for creating and listing users, containerized
with Docker Compose and using Alembic (via Flask-Migrate) for schema
migrations.

## Endpoints

### `POST /user`

Create a user. Requires `Content-Type: application/json` and a JSON object
body with a non-empty, non-blank `name` string of at most 80 characters.

```bash
curl -X POST http://localhost:5000/user \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice"}'
# -> 201 {"message": "User created!"}
```

Validation failures return JSON errors:

| Condition | Status |
|---|---|
| Missing/wrong `Content-Type` | 415 |
| Body isn't valid JSON | 400 |
| Body isn't a JSON object | 400 |
| `name` missing, `null`, non-string, blank, or over 80 chars | 400 |

```bash
curl -X POST http://localhost:5000/user \
  -H "Content-Type: application/json" \
  -d '{"name": ""}'
# -> 400 {"error": "\"name\" must not be blank"}
```

### `GET /users`

List all users.

```bash
curl http://localhost:5000/users
# -> 200 [{"id": 1, "name": "Alice"}]
```

## Running with Docker Compose

1. Copy `.env.example` to `.env` and adjust if needed:

   ```bash
   cp .env.example .env
   ```

2. Build and start:

   ```bash
   docker compose up --build
   ```

   The `app` service waits for the `db` service to report healthy, then the
   container's entrypoint waits for Postgres to accept connections, runs
   `flask db upgrade` to create/update the schema, and starts gunicorn.

3. The API is now available at `http://localhost:5000`.

## Database migrations

Migrations live in `migrations/` and are managed with `flask db` (Flask-Migrate,
wrapping Alembic). The compose entrypoint runs `flask db upgrade`
automatically on every start, so day-to-day usage of `docker compose up`
needs nothing further.

To create a new migration after changing a model, run against a database
you have `DATABASE_URL` pointed at:

```bash
export FLASK_APP=app.py
export DATABASE_URL=postgresql://user:password@localhost:5432/mydatabase
flask db migrate -m "describe the change"
flask db upgrade
```

Review the generated file under `migrations/versions/` before committing it
- autogenerate is a starting point, not a guarantee.

## Running tests

```bash
pip install -r requirements-dev.txt
pytest
```

Tests run against an in-memory SQLite database by default (set by
`conftest.py`, overriding any `DATABASE_URL` already in your environment).
To point the suite at a real database instead, set `TEST_DATABASE_URL`
before running `pytest`.

## Configuration

All configuration is via environment variables (see `.env.example`):

| Variable | Used by | Purpose |
|---|---|---|
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | `db` service | Initializes the Postgres container |
| `DATABASE_URL` | `app` service | SQLAlchemy connection string the app and `flask db` use |

## Caveats

- **Scaling `app` beyond one replica**: `flask db upgrade` runs from the
  container entrypoint on every start. With a single `app` service (the
  default here) that's harmless. If you scale `app` to multiple replicas,
  they will race to run the same migration concurrently on startup - move
  the migration into its own one-shot job/step before starting the app
  replicas rather than relying on the entrypoint if you do this.
- **`.env.example` duplicates credentials**: `POSTGRES_USER` /
  `POSTGRES_PASSWORD` / `POSTGRES_DB` and `DATABASE_URL` encode the same
  credentials in two places (the Postgres image needs the former, the app
  needs the latter as a connection string). They are not derived from one
  another, so editing one without the other will make them drift apart
  silently - keep them in sync by hand.
