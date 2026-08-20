def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "tony@example.com",
            "username": "tony",
            "password": "RallyPass123!",
            "skill_level": "intermediate",
            "preferred_position": "setter",
        },
    )


    assert response.status_code == 201


    data = response.json()


    assert data["email"] == (
        "tony@example.com"
    )

    assert data["username"] == "tony"

    assert data["skill_level"] == (
        "intermediate"
    )

    assert data[
        "preferred_position"
    ] == "setter"


    assert "password" not in data

    assert "password_hash" not in data


def test_duplicate_email_is_rejected(
    client,
):
    user_data = {
        "email": "tony@example.com",
        "username": "tony",
        "password": "RallyPass123!",
    }


    first_response = client.post(
        "/auth/register",
        json=user_data,
    )


    assert first_response.status_code == 201


    second_response = client.post(
        "/auth/register",
        json={
            "email": "tony@example.com",
            "username": "differentuser",
            "password": "AnotherPass123!",
        },
    )


    assert (
        second_response.status_code
        == 409
    )


def test_login(client):
    client.post(
        "/auth/register",
        json={
            "email": "tony@example.com",
            "username": "tony",
            "password": "RallyPass123!",
        },
    )


    response = client.post(
        "/auth/login",
        data={
            "username": "tony",
            "password": "RallyPass123!",
        },
    )


    assert response.status_code == 200


    data = response.json()


    assert "access_token" in data

    assert data["token_type"] == "bearer"


def test_wrong_password_is_rejected(
    client,
):
    client.post(
        "/auth/register",
        json={
            "email": "tony@example.com",
            "username": "tony",
            "password": "RallyPass123!",
        },
    )


    response = client.post(
        "/auth/login",
        data={
            "username": "tony",
            "password": "wrongpassword",
        },
    )


    assert response.status_code == 401