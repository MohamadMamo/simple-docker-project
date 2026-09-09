#!/bin/sh
set -e
python - <<'PY'
import os, sys, time, sqlalchemy as sa
engine = sa.create_engine(os.environ["DATABASE_URL"])
for attempt in range(1, 31):
    try:
        with engine.connect() as c:
            c.execute(sa.text("SELECT 1"))
        print(f"database ready after {attempt} attempt(s)", flush=True); break
    except Exception as exc:
        print(f"waiting for database ({attempt}/30): {type(exc).__name__}", flush=True)
        time.sleep(1)
else:
    print("database not ready after 30s", file=sys.stderr); sys.exit(1)
PY
flask db upgrade
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --access-logfile - --error-logfile - app:app
