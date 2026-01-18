const API_BASE = "https://projetocloudcomputing.onrender.com";


let csrfToken = null;

async function fetchCsrfToken() {
  const res = await fetch(`${API_BASE}/api/csrf`, {
    method: "GET",
    credentials: "include", 
  });

  if (!res.ok) {
    throw new Error("Failed to get CSRF token");
  }

  const data = await res.json();
  csrfToken = data.csrf_token;
}

function getSelectedCourse() {
  const el = document.querySelector('input[name="course"]:checked');
  return el ? el.value : null;
}

document.addEventListener("DOMContentLoaded", async () => {
  const form = document.getElementById("registerForm");
  const msg = document.getElementById("msg");

  try {
    await fetchCsrfToken();
  } catch (e) {
    msg.textContent = "Error: could not start secure session.";
    console.error(e);
    return;
  }

  form.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    msg.textContent = "";

    const payload = {
      username: document.getElementById("username").value.trim(),
      studentNumber: document.getElementById("studentNumber").value.trim(),
      password: document.getElementById("password").value,
      age: Number(document.getElementById("age").value),
      course: getSelectedCourse(),
    };

    try {
      const res = await fetch(`${API_BASE}/api/register`, {
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
        msg.textContent = data.error || "Registration failed.";
        return;
      }

      msg.textContent = "Registered successfully! Redirecting...";
      setTimeout(() => {
        window.location.href = "login.html";
      }, 800);
    } catch (e) {
      console.error(e);
      msg.textContent = "Network error. Try again.";
    }
  });
});
