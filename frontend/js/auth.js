const registerForm =
    document.getElementById("register-form");


if (registerForm) {
    registerForm.addEventListener(
        "submit",
        handleRegister
    );
}


const loginForm =
    document.getElementById("login-form");


if (loginForm) {
    loginForm.addEventListener(
        "submit",
        handleLogin
    );
}


async function handleRegister(event) {
    event.preventDefault();

    const messageElement =
        document.getElementById(
            "register-message"
        );

    const email =
        document.getElementById(
            "email"
        ).value;

    const username =
        document.getElementById(
            "username"
        ).value;

    const password =
        document.getElementById(
            "password"
        ).value;

    const skillLevel =
        document.getElementById(
            "skill-level"
        ).value;

    const position =
        document.getElementById(
            "position"
        ).value;


    const userData = {
        email: email,
        username: username,
        password: password,
        skill_level:
            skillLevel || null,
        preferred_position:
            position || null,
    };


    try {
        const user = await apiRequest(
            "/auth/register",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json",
                },

                body: JSON.stringify(
                    userData
                ),
            }
        );


        showMessage(
            messageElement,
            `Welcome ${user.username}! Account created.`,
            "success"
        );


        setTimeout(function () {
            window.location.href =
                "login.html";
        }, 1000);

    } catch (error) {

        showMessage(
            messageElement,
            error.message,
            "error"
        );
    }
}


async function handleLogin(event) {
    event.preventDefault();

    console.log("Login form submitted");

    const messageElement =
        document.getElementById(
            "login-message"
        );

    const username =
        document.getElementById(
            "login-username"
        ).value;

    const password =
        document.getElementById(
            "login-password"
        ).value;


    const formData =
        new URLSearchParams();

    formData.append(
        "username",
        username
    );

    formData.append(
        "password",
        password
    );


    try {
        const response = await apiRequest(
            "/auth/login",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/x-www-form-urlencoded",
                },

                body: formData.toString(),
            }
        );


        console.log(
            "Login response:",
            response
        );


        saveToken(
            response.access_token
        );


        showMessage(
            messageElement,
            "Login successful!",
            "success"
        );


        setTimeout(function () {
            window.location.href =
                "games.html";
        }, 700);

    } catch (error) {

        console.error(
            "Login failed:",
            error
        );


        showMessage(
            messageElement,
            error.message,
            "error"
        );
    }
}


function showMessage(
    element,
    message,
    type
) {
    if (!element) {
        return;
    }

    element.textContent = message;

    element.classList.remove(
        "hidden",
        "error",
        "success"
    );

    element.classList.add(type);
}