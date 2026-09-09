def test_get_users_empty_returns_empty_list(client):
    response = client.get("/users")
    assert response.status_code == 200
    assert response.get_json() == []


def test_get_users_shape(client):
    client.post("/user", json={"name": "Dana"})

    response = client.get("/users")
    assert response.status_code == 200
    body = response.get_json()
    assert isinstance(body, list)
    assert len(body) == 1
    assert set(body[0].keys()) == {"id", "name"}
    assert body[0]["name"] == "Dana"
