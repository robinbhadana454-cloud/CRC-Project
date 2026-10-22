from fastapi.testclient import TestClient


def test_register_user_success(client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newpassenger@example.com",
            "password": "StrongPassword123!",
            "full_name": "Priya Verma",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newpassenger@example.com"
    assert data["full_name"] == "Priya Verma"
    assert data["role"] == "passenger"
    assert "hashed_password" not in data


def test_register_duplicate_email_fails(client: TestClient):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "dup@example.com",
            "password": "Password123!",
            "full_name": "First User",
        },
    )
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "dup@example.com",
            "password": "AnotherPassword123!",
            "full_name": "Second User",
        },
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_login_success(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "passenger@test.com",
            "password": "PassengerPass123!",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "passenger@test.com"


def test_login_invalid_password(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "passenger@test.com",
            "password": "WrongPassword123!",
        },
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_unauthorized_profile_access(client: TestClient):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_authorized_profile_access(client: TestClient, passenger_headers: dict):
    response = client.get("/api/v1/auth/me", headers=passenger_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "passenger@test.com"
    assert data["role"] == "passenger"


def test_logout_and_token_revocation(client: TestClient, passenger_token: str):
    headers = {"Authorization": f"Bearer {passenger_token}"}
    # Verify token works before logout
    check1 = client.get("/api/v1/auth/me", headers=headers)
    assert check1.status_code == 200

    # Execute logout
    logout_res = client.post("/api/v1/auth/logout", headers=headers)
    assert logout_res.status_code == 200
    assert "revoked" in logout_res.json()["message"]

    # Verify token is now rejected after logout
    check2 = client.get("/api/v1/auth/me", headers=headers)
    assert check2.status_code == 401
    assert "revoked" in check2.json()["detail"]


def test_forgot_and_reset_password_flow(client: TestClient):
    # 1. Request forgot password
    forgot_res = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "passenger@test.com"},
    )
    assert forgot_res.status_code == 200
    reset_token = forgot_res.json()["reset_token"]
    assert reset_token is not None

    # 2. Reset password using the token
    reset_res = client.post(
        "/api/v1/auth/reset-password",
        json={"token": reset_token, "new_password": "NewSecretPassword99!"},
    )
    assert reset_res.status_code == 200
    assert "successfully reset" in reset_res.json()["message"]

    # 3. Old password should fail
    old_login = client.post(
        "/api/v1/auth/login",
        json={"email": "passenger@test.com", "password": "PassengerPass123!"},
    )
    assert old_login.status_code == 401

    # 4. New password should succeed
    new_login = client.post(
        "/api/v1/auth/login",
        json={"email": "passenger@test.com", "password": "NewSecretPassword99!"},
    )
    assert new_login.status_code == 200

    # 5. Reusing the same reset token must fail
    reuse_res = client.post(
        "/api/v1/auth/reset-password",
        json={"token": reset_token, "new_password": "AnotherPassword123!"},
    )
    assert reuse_res.status_code == 400
    assert "already been used" in reuse_res.json()["detail"]
