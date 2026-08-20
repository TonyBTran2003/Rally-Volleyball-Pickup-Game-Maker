def test_create_game(
    client,
    auth_headers,
):
    response = client.post(
        "/games",
        headers=auth_headers,
        json={
            "title":
                "Friday Night Volleyball",

            "description":
                "Intermediate pickup",

            "location":
                "Main Recreation Center",

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


    assert response.status_code == 201


    data = response.json()


    assert (
        data["title"]
        == "Friday Night Volleyball"
    )

    assert data["current_players"] == 1

    assert data["max_players"] == 12


def test_create_game_requires_login(
    client,
):
    response = client.post(
        "/games",
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


    assert response.status_code == 401