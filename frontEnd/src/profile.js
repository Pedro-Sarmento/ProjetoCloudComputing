const API_BASE = "https://projeto-cloud-backend.onrender.com";


async function loadMe() {
  const res = await fetch(`${API_BASE}/api/me`, { credentials: "include" });
  const data = await res.json();

  if (!data.logged_in) {
    window.location.href = "login.html";
    return;
  }

  const p = data.profile || {};
  document.getElementById("username").textContent = p.username || "";
  document.getElementById("studentNumber").textContent = p.studentNumber || "";
  document.getElementById("course").textContent = p.course || "";
  document.getElementById("age").textContent = p.age ?? "";
}

document.addEventListener("DOMContentLoaded", loadMe);

async function fetchCsrfToken() {
    const res = await fetch(`${API_BASE}/api/csrf`, { credentials: "include" });
    const data = await res.json();
    return data.csrf_token;
  }
  
  document.addEventListener("DOMContentLoaded", async () => {
    await loadMe();
  
    const logoutLink = document.getElementById("logoutLink");
    if (logoutLink) {
      logoutLink.addEventListener("click", async (e) => {
        e.preventDefault();
        const csrf = await fetchCsrfToken();
  
        await fetch(`${API_BASE}/api/logout`, {
          method: "POST",
          credentials: "include",
          headers: { "X-CSRF-Token": csrf },
        });
  
        window.location.href = "login.html";
      });
    }
  });
