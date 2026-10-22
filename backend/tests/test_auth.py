def test_register(client):
    resp = client.post("/api/auth/register", json={
        "email": "new@example.com",
        "full_name": "New User",
        "password": "securepass1",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["email"] == "new@example.com"

def test_register_duplicate(client, test_user):
    resp = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "full_name": "Dup",
        "password": "securepass1",
    })
    assert resp.status_code == 400

def test_login(client, test_user):
    resp = client.post("/api/auth/login", data={
        "username": "test@example.com",
        "password": "testpass123",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()

def test_login_wrong_password(client, test_user):
    resp = client.post("/api/auth/login", data={
        "username": "test@example.com",
        "password": "wrong",
    })
    assert resp.status_code == 401

def test_me_unauthorized(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401

def test_me_authorized(client, auth_headers):
    resp = client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@example.com"
