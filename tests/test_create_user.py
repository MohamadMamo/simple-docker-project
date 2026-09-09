import pytest


def test_post_user_returns_201(client):
    response = client.post("/user", json={"name": "Alice"})
    assert response.status_code == 201


def test_post_then_get_roundtrip(client):
    post_response = client.post("/user", json={"name": "Bob"})
    assert post_response.status_code == 201

    get_response = client.get("/users")
    assert get_response.status_code == 200
    names = [user["name"] for user in get_response.get_json()]
    assert "Bob" in names


def test_post_without_content_type_rejected(client, wrong_content_type_status):
    response = client.post("/user", data='{"name": "Carol"}')
    assert response.status_code == wrong_content_type_status


def test_post_empty_body_returns_400(client):
    response = client.post("/user", data="", content_type="application/json")
    assert response.status_code == 400


def test_post_malformed_json_returns_400(client):
    response = client.post("/user", data="{not valid json", content_type="application/json")
    assert response.status_code == 400


def test_missing_name_key_currently_raises_keyerror(client):
    """No input validation exists yet: a body with no "name" key currently
    blows up with an unhandled KeyError, surfaced to the client as a 500."""
    response = client.post("/user", json={})
    assert response.status_code == 500


@pytest.mark.parametrize("payload", [[1, 2], "hello", 42])
def test_non_object_json_currently_raises_typeerror(client, payload):
    """No input validation exists yet: top-level JSON that isn't an object
    currently blows up with an unhandled TypeError, surfaced as a 500."""
    response = client.post("/user", json=payload)
    assert response.status_code == 500


def test_null_name_currently_raises_integrityerror(client):
    """No input validation exists yet: an explicit null name currently
    blows up with an unhandled IntegrityError, surfaced as a 500."""
    response = client.post("/user", json={"name": None})
    assert response.status_code == 500
