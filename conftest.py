import importlib.metadata
import os

# Set BEFORE importing app, unconditionally: a developer's ambient
# DATABASE_URL must never let the test suite write to a real database.
os.environ["DATABASE_URL"] = os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:")

import pytest

from app import app as flask_app, db

# Never use flask.__version__ - it is deprecated and slated for removal.
_FLASK_MAJOR = int(importlib.metadata.version("flask").split(".")[0])
WRONG_CONTENT_TYPE_STATUS = 415 if _FLASK_MAJOR >= 3 else 400


@pytest.fixture
def app_ctx():
    """App context with a freshly created schema, torn down after the test."""
    with flask_app.app_context():
        db.drop_all()
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app_ctx):
    return app_ctx.test_client()


@pytest.fixture
def bare_client():
    """Test client with no schema created - for exercising the missing-table path."""
    with flask_app.app_context():
        db.drop_all()
    return flask_app.test_client()


@pytest.fixture
def wrong_content_type_status():
    return WRONG_CONTENT_TYPE_STATUS
