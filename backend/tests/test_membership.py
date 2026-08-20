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


    login_response = client.post(
        "/auth/login",
        data={
            "username": username,
            "password": password,
        },
    )


    token = login_response.json()[
        "access_token"
    ]


    return {
        "Authorization":
            "Bearer {}".format(token)
    }


def test_join_game(client):
    tony_headers = (
        create_user_and_login(
            client,
            "tony@example.com",
            "tony",
            "RallyPass123!",
        )
    )


    alex_headers = (
        create_user_and_login(
            client,
            "alex@example.com",
            "alex",
            "AlexPass123!",
        )
    )


    game_response = client.post(
        "/games",
        headers=tony_headers,
        json={
            "title":
                "Friday Volleyball",

            "location":
                "Main Gym",

            "game_date":
                "2026-09-01",

            "start_time":
                "18:30:00",

            "max_players": 12,

            "skill_level":
                "intermediate",

            "format":
                "6v6",
        },
    )


    game_id = game_response.json()["id"]


    join_response = client.post(
        "/games/{}/join".format(
            game_id
        ),
        headers=alex_headers,
    )


    assert join_response.status_code == 200


    assert (
        join_response.json()[
            "current_players"
        ]
        == 2
    )


def test_duplicate_join_is_rejected(
    client,
):
    tony_headers = (
        create_user_and_login(
            client,
            "tony@example.com",
            "tony",
            "RallyPass123!",
        )
    )


    alex_headers = (
        create_user_and_login(
            client,
            "alex@example.com",
            "alex",
            "AlexPass123!",
        )
    )


    game_response = client.post(
        "/games",
        headers=tony_headers,
        json={
            "title":
                "Friday Volleyball",

            "location":
                "Main Gym",

            "game_date":
                "2026-09-01",

            "start_time":
                "18:30:00",

            "max_players": 12,

            "skill_level":
                "intermediate",

            "format": "6v6",
        },
    )


    game_id = game_response.json()["id"]


    first_join = client.post(
        "/games/{}/join".format(game_id),
        headers=alex_headers,
    )


    assert first_join.status_code == 200


    second_join = client.post(
        "/games/{}/join".format(game_id),
        headers=alex_headers,
    )


    assert second_join.status_code == 409