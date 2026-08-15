const API_URL = "http://localhost:8000";


function getToken() {
    return localStorage.getItem(
        "rally_token"
    );
}


function saveToken(token) {
    localStorage.setItem(
        "rally_token",
        token
    );
}


function removeToken() {
    localStorage.removeItem(
        "rally_token"
    );
}


async function apiRequest(
    endpoint,
    options = {}
) {
    const headers = {
        ...(options.headers || {}),
    };


    const token = getToken();


    if (token) {
        headers["Authorization"] =
            `Bearer ${token}`;
    }


    const response = await fetch(
        `${API_URL}${endpoint}`,
        {
            ...options,
            headers: headers,
        }
    );


    let data = null;


    const contentType =
        response.headers.get(
            "content-type"
        );


    if (
        contentType &&
        contentType.includes(
            "application/json"
        )
    ) {
        data = await response.json();
    }


    if (!response.ok) {

        const message =
            data &&
            data.detail
                ? data.detail
                : "Something went wrong";


        throw new Error(message);
    }


    return data;
}