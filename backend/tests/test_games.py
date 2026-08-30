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

def create_test_game(
    client,
    auth_headers,
    title,
    skill_level="intermediate",
    game_format="6v6",
):
    return client.post(
        "/games",
        headers=auth_headers,
        json={
            "title": title,
            "location": "Main Gym",
            "game_date": "2027-01-15",
            "start_time": "18:30:00",
            "max_players": 12,
            "skill_level": skill_level,
            "format": game_format,
        },
    )

def test_game_pagination(
    client,
    auth_headers,
):
    for number in range(5):
        create_test_game(
            client,
            auth_headers,
            "Game {}".format(number),
        )

    response = client.get(
        "/games?page=1&page_size=2"
    )

    assert response.status_code == 200

    games = response.json()

    assert len(games) == 2


def test_second_page(
    client,
    auth_headers,
):
    for number in range(5):
        create_test_game(
            client,
            auth_headers,
            "Game {}".format(number),
        )

    response = client.get(
        "/games?page=2&page_size=2"
    )

    assert response.status_code == 200

    games = response.json()

    assert len(games) == 2


def test_last_page(
    client,
    auth_headers,
):
    for number in range(5):
        create_test_game(
            client,
            auth_headers,
            "Game {}".format(number),
        )

    response = client.get(
        "/games?page=3&page_size=2"
    )

    assert response.status_code == 200

    games = response.json()

    assert len(games) == 1


def test_invalid_page_is_rejected(
    client,
):
    response = client.get(
        "/games?page=0"
    )

    assert response.status_code == 422



def test_page_size_limit(
    client,
):
    response = client.get(
        "/games?page_size=1000"
    )

    assert response.status_code == 422


def test_filter_games_by_skill_level(
    client,
    auth_headers,
):
    create_test_game(
        client,
        auth_headers,
        "Intermediate Game",
        skill_level="intermediate",
    )

    create_test_game(
        client,
        auth_headers,
        "Advanced Game",
        skill_level="advanced",
    )

    response = client.get(
        "/games?skill_level=advanced"
    )

    assert response.status_code == 200

    games = response.json()

    assert len(games) == 1
    assert games[0]["title"] == "Advanced Game"
    assert games[0]["skill_level"] == "advanced"



def test_filter_games_by_format(
    client,
    auth_headers,
):
    create_test_game(
        client,
        auth_headers,
        "Sixes",
        game_format="6v6",
    )

    create_test_game(
        client,
        auth_headers,
        "Beach Doubles",
        game_format="2v2",
    )

    response = client.get(
        "/games?format=2v2"
    )

    assert response.status_code == 200

    games = response.json()

    assert len(games) == 1
    assert games[0]["format"] == "2v2"


def test_combined_game_filters(
    client,
    auth_headers,
):
    create_test_game(
        client,
        auth_headers,
        "Game A",
        skill_level="intermediate",
        game_format="6v6",
    )

    create_test_game(
        client,
        auth_headers,
        "Game B",
        skill_level="advanced",
        game_format="6v6",
    )

    create_test_game(
        client,
        auth_headers,
        "Game C",
        skill_level="advanced",
        game_format="2v2",
    )

    response = client.get(
        "/games"
        "?skill_level=advanced"
        "&format=6v6"
    )

    assert response.status_code == 200

    games = response.json()

    assert len(games) == 1
    assert games[0]["title"] == "Game B"


def test_game_list_has_correct_player_count(
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

    client.post(
        "/games/{}/join".format(
            game_id
        ),
        headers=alex_headers,
    )

    response = client.get(
        "/games"
    )

    assert response.status_code == 200

    games = response.json()

    assert len(games) == 1
    assert games[0]["current_players"] == 2



def test_non_creator_cannot_update_game(
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

    game_response = client.post(
        "/games",
        headers=tony_headers,
        json={
            "title": "Tony's Game",
            "location": "Main Gym",
            "game_date": "2027-01-15",
            "start_time": "18:30:00",
            "max_players": 12,
            "skill_level": "intermediate",
            "format": "6v6",
        },
    )

    game_id = game_response.json()["id"]

    response = client.patch(
        "/games/{}".format(game_id),
        headers=alex_headers,
        json={
            "title": "Alex Tried To Change This",
        },
    )

    assert response.status_code == 403


def test_non_creator_cannot_delete_game(
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

    game_response = client.post(
        "/games",
        headers=tony_headers,
        json={
            "title": "Protected Game",
            "location": "Main Gym",
            "game_date": "2027-01-15",
            "start_time": "18:30:00",
            "max_players": 12,
            "skill_level": "intermediate",
            "format": "6v6",
        },
    )

    game_id = game_response.json()["id"]

    response = client.delete(
        "/games/{}".format(game_id),
        headers=alex_headers,
    )

    assert response.status_code == 403