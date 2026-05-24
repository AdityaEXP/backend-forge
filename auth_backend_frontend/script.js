const loginForm = document.getElementById("login-form");
const signupForm = document.getElementById("signup-form");
const viewProfileButton = document.getElementById("view-profile");
const refreshButton = document.getElementById("refresh-token");
const clearTokenButton = document.getElementById("clear-token");
const logoutButton = document.getElementById("logout");
const output = document.getElementById("output");
const requestStatus = document.getElementById("request-status");
const tokenState = document.getElementById("token-state");
const baseUrlInput = document.getElementById("api-base-url");

const tokenStorageKey = "token";

syncTokenState();

loginForm.addEventListener("submit", handleLogin);
signupForm.addEventListener("submit", handleSignup);
viewProfileButton.addEventListener("click", handleViewProfile);
refreshButton.addEventListener("click", handleRefreshSession);
clearTokenButton.addEventListener("click", handleClearToken);
logoutButton.addEventListener("click", handleLogout);

function getBaseUrl() {
    return baseUrlInput.value.trim().replace(/\/$/, "");
}

function setStatus(type, message) {
    const dot = requestStatus.querySelector(".dot");
    const label = requestStatus.querySelector("span:last-child");

    dot.className = "dot";
    if (type === "ok") {
        dot.classList.add("ok");
    } else if (type === "error") {
        dot.classList.add("err");
    }

    label.textContent = message;
}

function showOutput(title, payload) {
    output.textContent = `${title}\n\n${typeof payload === "string" ? payload : JSON.stringify(payload, null, 2)}`;
}

function getToken() {
    return localStorage.getItem(tokenStorageKey);
}

function syncTokenState() {
    const token = getToken();
    tokenState.textContent = token ? `${token.slice(0, 18)}...` : "not saved";
}

function saveToken(token) {
    localStorage.setItem(tokenStorageKey, token);
    syncTokenState();
}

function clearToken() {
    localStorage.removeItem(tokenStorageKey);
    syncTokenState();
}

async function requestJson(path, options = {}) {
    const response = await fetch(`${getBaseUrl()}${path}`, {
        credentials: "include",
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {})
        },
        ...options
    });

    const rawText = await response.text();
    let data = rawText;

    if (rawText) {
        try {
            data = JSON.parse(rawText);
        } catch {
            data = rawText;
        }
    }

    return { response, data };
}

async function handleSignup(event) {
    event.preventDefault();
    setStatus("", "Creating user...");

    const payload = {
        username: document.getElementById("signup-username").value.trim(),
        email: document.getElementById("signup-email").value.trim(),
        password: document.getElementById("signup-password").value
    };

    const { response, data } = await requestJson("/auth/signup", {
        method: "POST",
        body: JSON.stringify(payload)
    });

    showOutput(`POST /auth/signup -> ${response.status}`, data);

    if (!response.ok) {
        setStatus("error", data?.detail || "Sign up failed");
        return;
    }

    setStatus("ok", "Sign up successful");
}

async function handleLogin(event) {
    event.preventDefault();
    setStatus("", "Logging in...");

    const payload = {
        email: document.getElementById("login-email").value.trim(),
        password: document.getElementById("login-password").value
    };

    const { response, data } = await requestJson("/auth/login", {
        method: "POST",
        body: JSON.stringify(payload)
    });

    showOutput(`POST /auth/login -> ${response.status}`, data);

    if (!response.ok) {
        setStatus("error", data?.detail || "Login failed");
        return;
    }

    if (data?.access_token) {
        saveToken(data.access_token);
    }

    setStatus("ok", "Login successful");
}

async function handleViewProfile() {
    const token = getToken();

    if (!token) {
        setStatus("error", "No saved token yet");
        showOutput("GET /users/me", "Missing access token. Log in first.");
        return;
    }

    setStatus("", "Loading profile...");

    const { response, data } = await requestJson("/users/me", {
        method: "GET",
        headers: {
            Authorization: `Bearer ${token}`
        }
    });

    showOutput(`GET /users/me -> ${response.status}`, data);

    if (!response.ok) {
        setStatus("error", data?.detail || "Profile request failed");
        return;
    }

    setStatus("ok", `Loaded profile for ${data.username}`);
}

async function handleRefreshSession() {
    setStatus("", "Refreshing session...");

    const { response, data } = await requestJson("/auth/refresh", {
        method: "POST"
    });

    showOutput(`POST /auth/refresh -> ${response.status}`, data);

    if (!response.ok) {
        setStatus("error", data?.detail || "Refresh failed");
        return;
    }

    if (data?.access_token) {
        saveToken(data.access_token);
    }

    setStatus("ok", "Session refreshed");
}

async function handleLogout() {
    setStatus("", "Logging out...");

    const { response, data } = await requestJson("/auth/logout", {
        method: "POST"
    });

    showOutput(`POST /auth/logout -> ${response.status}`, data);

    if (!response.ok) {
        setStatus("error", data?.detail || "Logout failed");
        return;
    }

    // clearToken(); Don't clear token on logout since it might still be valid until expiry. Let user decide when to clear it.
    setStatus("ok", data?.message || "Logged out");
}

function handleClearToken() {
    clearToken();
    setStatus("ok", "Token cleared");
    showOutput("Local state", "Access token removed from localStorage.");
}