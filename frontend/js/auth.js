document.addEventListener("DOMContentLoaded", () => {
    const API_BASE = "http://127.0.0.1:8080"; // backend adresin
    const loginForm = document.getElementById("login-form");
    const registerForm = document.getElementById("register-form");
  
    document.getElementById("showRegister").addEventListener("click", (e) => {
      e.preventDefault();
      loginForm.style.display = "none";
      registerForm.style.display = "block";
    });
  
    document.getElementById("showLogin").addEventListener("click", (e) => {
      e.preventDefault();
      registerForm.style.display = "none";
      loginForm.style.display = "block";
    });

    // ✅ Login
    document.getElementById("loginForm").addEventListener("submit", async (e) => {
      e.preventDefault();
  
      const email = document.getElementById("loginEmail").value;
      const password = document.getElementById("loginPassword").value;

      try {
        const res = await fetch(`${API_BASE}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: new URLSearchParams({
              username: email,
              password: password,
            }),
          });
  
        if (!res.ok) {
          const errorData = await res.json();
          alert(`Login failed: ${errorData.detail || "Unknown error"}`);
          return;
        }
  
        const data = await res.json();
        console.log("Login Success:", data);
  
        // Tokenları sakla
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("refresh_token", data.refresh_token);
  
        // ✅ Projects sayfasına yönlendir
        window.location.href = "projects.html";
  
      } catch (err) {
        console.error("Login Error:", err);
        alert("Login request failed.");
      }
    });
  
    // ✅ Register
    // ✅ Register
document.getElementById("registerForm").addEventListener("submit", async (e) => {
    e.preventDefault();
  
    const payload = {
      username: document.getElementById("regUsername").value,
      email: document.getElementById("regEmail").value,
      password: document.getElementById("regPassword").value,
    };
  
    try {
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
  
      if (!res.ok) {
        const errorData = await res.json();
        alert(`Register failed: ${errorData.detail || "Unknown error"}`);
        return;
      }
  
      const data = await res.json();
      console.log("Register Success:", data);
  
      alert("Registration successful! You can now login.");
      // Register sonrası login ekranına dön
      registerForm.style.display = "none";
      loginForm.style.display = "block";
  
    } catch (err) {
      console.error("Register Error:", err);
      alert("Register request failed.");
    }
  });  
  });
  