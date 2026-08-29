document.addEventListener(
    "DOMContentLoaded",
    initializeEditPage
);


function getGameId() {
    const params =
        new URLSearchParams(
            window.location.search
        );

    return params.get("id");
}


async function initializeEditPage() {
    if (!getToken()) {
        window.location.href =
            "login.html";

        return;
    }

    const gameId = getGameId();

    if (!gameId) {
        showEditMessage(
            "No game was selected.",
            "error"
        );

        return;
    }

    try {
        const results =
            await Promise.all([
                apiRequest("/users/me"),
                apiRequest(
                    `/games/${gameId}`
                ),
            ]);

        const currentUser = results[0];
        const game = results[1];

        if (
            game.creator_id !==
            currentUser.id
        ) {
            showEditMessage(
                "You are not allowed to edit this game.",
                "error"
            );

            return;
        }

        populateGameForm(game);

        document
            .getElementById(
                "edit-game-form"
            )
            .addEventListener(
                "submit",
                handleEditGame
            );

        setupEditLogout();

    } catch (error) {
        showEditMessage(
            error.message,
            "error"
        );
    }
}


function populateGameForm(game) {
    document.getElementById(
        "game-title"
    ).value = game.title;

    document.getElementById(
        "game-description"
    ).value =
        game.description || "";

    document.getElementById(
        "game-location"
    ).value = game.location;

    document.getElementById(
        "game-date"
    ).value = game.game_date;

    document.getElementById(
        "game-time"
    ).value =
        game.start_time.slice(0, 5);

    document.getElementById(
        "max-players"
    ).value = game.max_players;

    document.getElementById(
        "game-skill"
    ).value = game.skill_level;

    document.getElementById(
        "game-format"
    ).value = game.format;

    document.getElementById(
        "game-status"
    ).value = game.status;
}


async function handleEditGame(event) {
    event.preventDefault();

    const gameId = getGameId();

    const gameData = {
        title:
            document.getElementById(
                "game-title"
            ).value,

        description:
            document.getElementById(
                "game-description"
            ).value || null,

        location:
            document.getElementById(
                "game-location"
            ).value,

        game_date:
            document.getElementById(
                "game-date"
            ).value,

        start_time:
            document.getElementById(
                "game-time"
            ).value,

        max_players:
            Number(
                document.getElementById(
                    "max-players"
                ).value
            ),

        skill_level:
            document.getElementById(
                "game-skill"
            ).value,

        format:
            document.getElementById(
                "game-format"
            ).value,

        status:
            document.getElementById(
                "game-status"
            ).value,
    };

    try {
        await apiRequest(
            `/games/${gameId}`,
            {
                method: "PATCH",

                headers: {
                    "Content-Type":
                        "application/json",
                },

                body:
                    JSON.stringify(
                        gameData
                    ),
            }
        );

        showEditMessage(
            "Game updated successfully!",
            "success"
        );

        setTimeout(
            function () {
                window.location.href =
                    "games.html";
            },
            700
        );

    } catch (error) {
        showEditMessage(
            error.message,
            "error"
        );
    }
}


function showEditMessage(
    message,
    type
) {
    const element =
        document.getElementById(
            "edit-game-message"
        );

    element.textContent = message;

    element.classList.remove(
        "hidden",
        "success",
        "error"
    );

    element.classList.add(type);
}


function setupEditLogout() {
    const button =
        document.getElementById(
            "logout-button"
        );

    if (!button) {
        return;
    }

    button.addEventListener(
        "click",
        function () {
            removeToken();

            window.location.href =
                "login.html";
        }
    );
}