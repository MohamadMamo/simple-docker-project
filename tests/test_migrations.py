import os
import subprocess
import sys
import tempfile

from alembic.migration import MigrationContext
from alembic.autogenerate import compare_metadata
from sqlalchemy import create_engine

from app import db


def test_migrations_produce_the_model_schema():
    """Running the committed migrations against a fresh DB must produce
    exactly the schema the SQLAlchemy models declare - no drift."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "migration_check.db")
        database_url = f"sqlite:///{db_path}"

        env = os.environ.copy()
        env["DATABASE_URL"] = database_url
        env["FLASK_APP"] = "app.py"

        subprocess.run(
            [sys.executable, "-m", "flask", "db", "upgrade"],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )

        engine = create_engine(database_url)
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            diff = compare_metadata(context, db.metadata)

        assert diff == []
