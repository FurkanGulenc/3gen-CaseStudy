document.addEventListener("DOMContentLoaded", () => {
    const API_BASE = "http://127.0.0.1:8080"; 
    const token = localStorage.getItem("access_token");
    const tableBody = document.querySelector("#projectsTable tbody");
  
    // -------------------------------
    // 📌 Logout
    // -------------------------------
    const logoutBtn = document.getElementById("logoutBtn");
    if (logoutBtn) {
      logoutBtn.addEventListener("click", () => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.replace("/"); // Root'a yönlendir
      });
    }
  
    // -------------------------------
    // 📌 Popup aç/kapat
    // -------------------------------
    const openPopupBtn = document.getElementById("openPopup");
    const closePopupBtn = document.getElementById("closePopup");
    const popupOverlay = document.getElementById("popupOverlay");
  
    openPopupBtn.addEventListener("click", () => {
      popupOverlay.style.display = "flex";
    });
  
    closePopupBtn.addEventListener("click", () => {
      popupOverlay.style.display = "none";
    });
  
    popupOverlay.addEventListener("click", (e) => {
      if (e.target === popupOverlay) {
        popupOverlay.style.display = "none";
      }
    });
  
    // -------------------------------
    // 📌 Yeni proje oluşturma
    // -------------------------------
    const form = document.getElementById("newProjectForm");
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
  
      const formData = new FormData();
      formData.append("name", document.getElementById("projectName").value);
      formData.append("feed_url", document.getElementById("feedUrl").value);
      formData.append("frame_image", document.getElementById("frameUpload").files[0]);
  
      try {
        const res = await fetch(`${API_BASE}/projects/create`, {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${token}`,
            // FormData gönderirken Content-Type elleme!
          },
          body: formData
        });
  
        const text = await res.text();
        console.log("Response status:", res.status);
        console.log("Response text:", text);
  
        if (!res.ok) {
          alert("Project creation failed!");
          return;
        }
  
        alert("Project created successfully!");
        popupOverlay.style.display = "none";
        form.reset();
        fetchProjects();
      } catch (err) {
        console.error("Error creating project:", err);
        alert("Project creation error!");
      }
    });
  
    // -------------------------------
    // 📌 Projeleri Listele
    // -------------------------------
    async function fetchProjects() {
      try {
        const res = await fetch(`${API_BASE}/projects/get-projects`, {
          method: "GET",
          headers: {
            "Authorization": `Bearer ${token}`,
          },
        });
  
        if (!res.ok) {
          console.error("Projects fetch failed", await res.text());
          return;
        }
  
        const projects = await res.json();
        renderProjects(projects);
      } catch (err) {
        console.error("Error fetching projects:", err);
      }
    }
  
    function renderProjects(projects) {
      tableBody.innerHTML = ""; // temizle
  
      projects.forEach((project) => {
        const tr = document.createElement("tr");
  
        tr.innerHTML = `
          <td>${project.name}</td>
          <td><a href="${project.feed_url}" target="_blank">${project.feed_url}</a></td>
          <td>${new Date(project.created_at).toLocaleString()}</td>
          <td>
            <button onclick="viewProject('${project.id}')">View</button>
          </td>
        `;
  
        tableBody.appendChild(tr);
      });
  
      // DataTables init (önceden init edilmişse destroy et)
      if ($.fn.DataTable.isDataTable("#projectsTable")) {
        $("#projectsTable").DataTable().clear().destroy();
      }
      $("#projectsTable").DataTable({
        paging: true,
        searching: true,
        ordering: true,
        pageLength: 5,
        lengthMenu: [5, 10, 25, 50],
      });
    }
  
    // -------------------------------
    // 📌 View Project yönlendirme
    // -------------------------------
    window.viewProject = function (id) {
      window.location.href = `project_details.html?id=${id}`;
    };
  
    // -------------------------------
    // 📌 Sayfa yüklenince başlat
    // -------------------------------
    fetchProjects();
  });
  