const API_BASE = "https://projeto-cloud-backend.onrender.com";

let csrfToken = null;

async function fetchCsrfToken() {
  const res = await fetch(`${API_BASE}/api/csrf`, {
    method: "GET",
    credentials: "include",
  });
  if (!res.ok) throw new Error("Failed to get CSRF token");
  const data = await res.json();
  csrfToken = data.csrf_token;
}

document.addEventListener("DOMContentLoaded", async () => {
  const form = document.getElementById("loginForm");
  const msg = document.getElementById("msg");

  try {
    await fetchCsrfToken();
  } catch (e) {
    console.error(e);
    msg.textContent = "Error: could not start secure session.";
    return;
  }

  form.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    msg.textContent = "";

    const payload = {
      username: document.getElementById("username").value.trim(),
      password: document.getElementById("password").value,
    };

    try {
      const res = await fetch(`${API_BASE}/api/login`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-Token": csrfToken,
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        msg.textContent = data.error || "Login failed.";
        return;
      }

      msg.textContent = "Logged in! Redirecting...";
      setTimeout(() => {
        window.location.href = "profile.html";
      }, 600);
    } catch (e) {
      console.error(e);
      msg.textContent = "Network error. Try again.";
    }
  });
});
