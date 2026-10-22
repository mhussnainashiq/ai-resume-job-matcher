from app.models.user import User
from app.core.security import get_password_hash

def test_cross_user_resume_isolation(client, db, auth_headers, test_user):
    # Create second user
    user2 = User(email="other@example.com", full_name="Other", hashed_password=get_password_hash("pass12345"))
    db.add(user2)
    db.commit()

    # Login as user2
    resp = client.post("/api/auth/login", data={"username": "other@example.com", "password": "pass12345"})
    token2 = resp.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # User1 list resumes (empty)
    r1 = client.get("/api/resumes", headers=auth_headers)
    assert r1.status_code == 200
    assert r1.json()["total"] == 0

    # User2 cannot access a non-existent resume of user1
    r2 = client.get("/api/resumes/999", headers=headers2)
    assert r2.status_code == 404
