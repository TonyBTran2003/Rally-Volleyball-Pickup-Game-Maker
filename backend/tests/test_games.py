def create_user_and_login(
    client,
    email,
    username,
    password,
):
    client.post(
        "/auth/register",
        json={
            "email": email,
            "username": username,
            "password": password,
        },
    )

    response = client.post(
        "/auth/login",
        data={
            "username": username,
            "password": password,
        },
    )

    token = response.json()["access_token"]

    return {
        "Authorization":
            "Bearer {}".format(token)
    }


def test_create_game(
    client,
    auth_headers,
):
    response = client.post(
        "/games",
        headers=auth_headers,
        json={
            "title": "Friday Night Volleyball",
            "description": "Intermediate pickup",
            "location": "Main Recreation Center",
            "game_date": "2026-09-01",
            "start_time": "18:30:00",
            "max_players": 12,
            "skill_level": "intermediate",
            "format": "6v6",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Friday Night Volleyball"
    assert data["current_players"] == 1
    assert data["max_players"] == 12


def test_create_game_requires_login(
    client,
):
    response = client.post(
        "/games",
        json={
            "title": "Friday Volleyball",
            "location": "Main Gym",
            "game_date": "2026-09-01",
            "start_time": "18:30:00",
            "max_players": 12,
            "skill_level": "intermediate",
            "format": "6v6",
        },
    )

    assert response.status_code == 401


def test_create_game_in_past_is_rejected(
    client,
    auth_headers,
):
    response = client.post(
        "/games",
        headers=auth_headers,
        json={
            "title": "Old Game",
            "location": "Main Gym",
            "game_date": "2020-01-01",
            "start_time": "18:30:00",
            "max_players": 12,
            "skill_level": "intermediate",
            "format": "6v6",
        },
    )

    assert response.status_code == 400


def test_blank_title_is_rejected(
    client,
    auth_headers,
):
    response = client.post(
        "/games",
        headers=auth_headers,
        json={
            "title": "   ",
            "location": "Main Gym",
            "game_date": "2027-01-01",
            "start_time": "18:30:00",
            "max_players": 12,
            "skill_level": "intermediate",
            "format": "6v6",
        },
    )

    assert response.status_code == 400


def test_cannot_lower_capacity_below_current_players(
    client,
):
    tony_headers = create_user_and_login(
        client,
        "tony@example.com",
        "tony",
        "RallyPass123!",
    )

    alex_headers = create_user_and_login(
        client,
        "alex@example.com",
        "alex",
        "AlexPass123!",
    )

    sam_headers = create_user_and_login(
        client,
        "sam@example.com",
        "sam",
        "SamPass123!",
    )

    game_response = client.post(
        "/games",
        headers=tony_headers,
        json={
            "title": "Friday Volleyball",
            "location": "Main Gym",
            "game_date": "2027-01-15",
            "start_time": "18:30:00",
            "max_players": 12,
            "skill_level": "intermediate",
            "format": "6v6",
        },
    )

    game_id = game_response.json()["id"]

    # Player #2
    client.post(
        "/games/{}/join".format(game_id),
        headers=alex_headers,
    )

    # Player #3
    client.post(
        "/games/{}/join".format(game_id),
        headers=sam_headers,
    )

    # Cannot reduce a 3-player game to capacity 2.
    response = client.patch(
        "/games/{}".format(game_id),
        headers=tony_headers,
        json={
            "max_players": 2,
        },
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "Maximum players cannot be "
        "lower than the current player count"
    )