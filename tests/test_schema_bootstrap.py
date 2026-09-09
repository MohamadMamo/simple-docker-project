from sqlalchemy import inspect

from app import db


def test_requests_fail_when_schema_absent(bare_client):
    """With no migrations/create_all ever run, a fresh DB has no tables and
    every request currently 500s instead of returning a useful error."""
    response = bare_client.get("/users")
    assert response.status_code == 500


def test_user_model_shape(app_ctx):
    inspector = inspect(db.engine)
    columns = {col["name"]: col for col in inspector.get_columns("user")}

    assert set(columns) == {"id", "name"}
    assert columns["id"]["primary_key"]
    assert columns["name"]["nullable"] is False
