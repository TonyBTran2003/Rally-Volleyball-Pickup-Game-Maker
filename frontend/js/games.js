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