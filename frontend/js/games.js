console.log("games.js loaded");


document.addEventListener(
    "DOMContentLoaded",
    function () {
        console.log("DOM loaded");

        loadCurrentUser();
        setupLogout();
    }
);


async function loadCurrentUser() {
    console.log("Loading current user...");

    const userElement =
        document.getElementById(
            "current-user"
        );

    if (!userElement) {
        console.error(
            "Could not find #current-user"
        );

        return;
    }


    try {
        const user = await apiRequest(
            "/users/me"
        );


        console.log(
            "Current user:",
            user
        );


        userElement.innerHTML = `
            <p>
                <strong>Username:</strong>
                ${user.username}
            </p>

            <p>
                <strong>Email:</strong>
                ${user.email}
            </p>

            <p>
                <strong>Skill:</strong>
                ${user.skill_level || "Not set"}
            </p>

            <p>
                <strong>Position:</strong>
                ${user.preferred_position || "Not set"}
            </p>
        `;

    } catch (error) {

        console.error(
            "Could not load user:",
            error
        );


        userElement.textContent =
            "You are not logged in.";


        setTimeout(
            function () {
                window.location.href =
                    "login.html";
            },
            1000
        );
    }
}


function setupLogout() {
    const logoutButton =
        document.getElementById(
            "logout-button"
        );


    if (!logoutButton) {
        console.error(
            "Could not find #logout-button"
        );

        return;
    }


    logoutButton.addEventListener(
        "click",
        function () {
            console.log("Logging out");

            removeToken();

            window.location.href =
                "login.html";
        }
    );
}


document.addEventListener(
    "DOMContentLoaded",
    function () {
        setupLogout();

        if (
            document.getElementById(
                "games-list"
            )
        ) {
            initializeGamesPage();
        }

        if (
            document.getElementById(
                "create-game-form"
            )
        ) {
            initializeCreateGamePage();
        }
    }
);


function setupLogout() {
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


async function initializeGamesPage() {
    if (!getToken()) {
        window.location.href =
            "login.html";

        return;
    }

    try {
        const results = await Promise.all([
            apiRequest("/users/me"),
            apiRequest("/games"),
            apiRequest("/users/me/games"),
        ]);

        const user = results[0];
        const games = results[1];
        const joinedGameIds = results[2];

        displayWelcomeMessage(user);

        renderGames(
            games,
            user,
            joinedGameIds
        );

    } catch (error) {
        console.error(error);

        showGamesMessage(
            error.message,
            "error"
        );
    }
}


function displayWelcomeMessage(user) {
    const element =
        document.getElementById(
            "welcome-message"
        );

    if (!element) {
        return;
    }

    element.textContent =
        `Welcome, ${user.username}`;
}


function renderGames(
    games,
    currentUser,
    joinedGameIds
) {
    const gamesList =
        document.getElementById(
            "games-list"
        );

    gamesList.innerHTML = "";


    if (games.length === 0) {
        gamesList.innerHTML = `
            <div class="card">
                <h2>No games yet</h2>

                <p>
                    Be the first person
                    to create a volleyball game.
                </p>
            </div>
        `;

        return;
    }


    const joinedSet =
        new Set(joinedGameIds);


    for (const game of games) {
        const card =
            createGameCard(
                game,
                currentUser,
                joinedSet.has(game.id)
            );

        gamesList.appendChild(card);
    }
}


function createGameCard(
    game,
    currentUser,
    hasJoined
) {
    const card =
        document.createElement("article");

    card.className =
        "game-card";


    const isCreator =
        game.creator_id === currentUser.id;


    const isFull =
        game.current_players >=
        game.max_players;


    const date =
        formatGameDate(
            game.game_date
        );


    const time =
        formatGameTime(
            game.start_time
        );


    let actionHtml = "";


    if (isCreator) {
        actionHtml = `
            <button
                class="delete-button"
                data-action="delete"
                data-game-id="${game.id}"
            >
                Delete Game
            </button>
        `;
    }

    else if (hasJoined) {
        actionHtml = `
            <button
                class="leave-button"
                data-action="leave"
                data-game-id="${game.id}"
            >
                Leave Game
            </button>
        `;
    }

    else if (
        isFull ||
        game.status !== "open"
    ) {
        actionHtml = `
            <button
                class="disabled-button"
                disabled
            >
                ${
                    isFull
                        ? "Game Full"
                        : "Unavailable"
                }
            </button>
        `;
    }

    else {
        actionHtml = `
            <button
                data-action="join"
                data-game-id="${game.id}"
            >
                Join Game
            </button>
        `;
    }


    card.innerHTML = `
        ${
            isCreator
                ? `
                    <span class="organizer-badge">
                        Organizer
                    </span>
                `
                : ""
        }

        <h2>
            ${escapeHtml(game.title)}
        </h2>

        <p class="game-description">
            ${
                escapeHtml(
                    game.description ||
                    "No description provided."
                )
            }
        </p>

        <div class="game-details">

            <p>
                <strong>Location:</strong>
                ${escapeHtml(game.location)}
            </p>

            <p>
                <strong>Date:</strong>
                ${date}
            </p>

            <p>
                <strong>Time:</strong>
                ${time}
            </p>

            <p>
                <strong>Players:</strong>
                ${game.current_players}
                /
                ${game.max_players}
            </p>

            <p>
                <strong>Skill:</strong>
                ${escapeHtml(game.skill_level)}
            </p>

            <p>
                <strong>Format:</strong>
                ${escapeHtml(game.format)}
            </p>

        </div>

        <div class="game-actions">
            ${actionHtml}
        </div>
    `;


    const actionButton =
        card.querySelector(
            "[data-action]"
        );


    if (actionButton) {
        actionButton.addEventListener(
            "click",
            handleGameAction
        );
    }


    return card;
}


function formatGameDate(dateString) {
    const parts =
        dateString.split("-");

    const date =
        new Date(
            Number(parts[0]),
            Number(parts[1]) - 1,
            Number(parts[2])
        );

    return date.toLocaleDateString(
        undefined,
        {
            weekday: "short",
            month: "short",
            day: "numeric",
            year: "numeric",
        }
    );
}


function formatGameTime(timeString) {
    const parts =
        timeString.split(":");

    const date =
        new Date();

    date.setHours(
        Number(parts[0]),
        Number(parts[1]),
        0
    );

    return date.toLocaleTimeString(
        undefined,
        {
            hour: "numeric",
            minute: "2-digit",
        }
    );
}


function escapeHtml(value) {
    const element =
        document.createElement("div");

    element.textContent =
        String(value);

    return element.innerHTML;
}


async function handleGameAction(event) {
    const button =
        event.currentTarget;

    const action =
        button.dataset.action;

    const gameId =
        button.dataset.gameId;


    button.disabled = true;


    try {

        if (action === "join") {
            await apiRequest(
                `/games/${gameId}/join`,
                {
                    method: "POST",
                }
            );

            showGamesMessage(
                "You joined the game!",
                "success"
            );
        }


        if (action === "leave") {
            await apiRequest(
                `/games/${gameId}/leave`,
                {
                    method: "DELETE",
                }
            );

            showGamesMessage(
                "You left the game.",
                "success"
            );
        }


        if (action === "delete") {

            const confirmed =
                window.confirm(
                    "Delete this game?"
                );


            if (!confirmed) {
                button.disabled = false;

                return;
            }


            await apiRequest(
                `/games/${gameId}`,
                {
                    method: "DELETE",
                }
            );


            showGamesMessage(
                "Game deleted.",
                "success"
            );
        }


        await initializeGamesPage();

    } catch (error) {

        showGamesMessage(
            error.message,
            "error"
        );


        button.disabled = false;
    }
}


function showGamesMessage(
    message,
    type
) {
    const element =
        document.getElementById(
            "games-message"
        );

    if (!element) {
        return;
    }

    element.textContent =
        message;

    element.classList.remove(
        "hidden",
        "error",
        "success"
    );

    element.classList.add(type);
}


function initializeCreateGamePage() {
    if (!getToken()) {
        window.location.href =
            "login.html";

        return;
    }


    const form =
        document.getElementById(
            "create-game-form"
        );


    setMinimumGameDate();


    form.addEventListener(
        "submit",
        handleCreateGame
    );
}


function setMinimumGameDate() {
    const dateInput =
        document.getElementById(
            "game-date"
        );

    if (!dateInput) {
        return;
    }


    const today =
        new Date();


    const year =
        today.getFullYear();


    const month =
        String(
            today.getMonth() + 1
        ).padStart(2, "0");


    const day =
        String(
            today.getDate()
        ).padStart(2, "0");


    dateInput.min =
        `${year}-${month}-${day}`;
}


async function handleCreateGame(event) {
    event.preventDefault();


    const messageElement =
        document.getElementById(
            "create-game-message"
        );


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
    };


    try {
        const game =
            await apiRequest(
                "/games",
                {
                    method: "POST",

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


        messageElement.textContent =
            `Game "${game.title}" created!`;

        messageElement.classList.remove(
            "hidden",
            "error"
        );

        messageElement.classList.add(
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

        messageElement.textContent =
            error.message;

        messageElement.classList.remove(
            "hidden",
            "success"
        );

        messageElement.classList.add(
            "error"
        );
    }
}