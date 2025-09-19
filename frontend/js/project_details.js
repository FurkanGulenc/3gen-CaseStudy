document.addEventListener("DOMContentLoaded", () => {
  const API_BASE = "http://127.0.0.1:8080";
  const token = localStorage.getItem("access_token");

  const urlParams = new URLSearchParams(window.location.search);
  const projectId = urlParams.get("id");

  // DOM
  const thumbnailsList = document.querySelector(".thumbnails-list");
  const posX = document.getElementById("posX");
  const posY = document.getElementById("posY");
  const width = document.getElementById("width");
  const height = document.getElementById("height");
  const radiusInput = document.getElementById("radius");
  const saveCoordsBtn = document.getElementById("saveCoords");
  const startProcessingBtn = document.getElementById("startProcessing");

  const canvas = new fabric.Canvas("editorCanvas", {
    preserveObjectStacking: true,
    selection: false,
    backgroundColor: "transparent",
  });

  let frameObj, productObj;

  // --- Frame metrics helper
  function getFrameMetrics() {
    if (!frameObj) return null;

    const drawnW = frameObj.getScaledWidth();
    const drawnH = frameObj.getScaledHeight();

    const frameTLx = frameObj.left - drawnW / 2;
    const frameTLy = frameObj.top - drawnH / 2;

    const kx = frameObj.width / drawnW;
    const ky = frameObj.height / drawnH;

    return { drawnW, drawnH, frameTLx, frameTLy, kx, ky };
  }

  // --- 1) Proje detayları
  async function fetchProjectDetails() {
    try {
      const res = await fetch(`${API_BASE}/projects/${projectId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        console.error("Project fetch failed:", await res.text());
        return;
      }
      const project = await res.json();

      // Frame
      fabric.Image.fromURL(project.frame_image, (img) => {
        frameObj = img;
        frameObj.selectable = false;
        frameObj.evented = false;

        const cw = canvas.getWidth();
        const ch = canvas.getHeight();

        const scaleX = cw / img.width;
        const scaleY = ch / img.height;
        const scale = Math.min(scaleX, scaleY);

        frameObj.scaleX = scale;
        frameObj.scaleY = scale;
        frameObj.originX = "center";
        frameObj.originY = "center";
        frameObj.left = cw / 2;
        frameObj.top = ch / 2;

        canvas.add(frameObj);
        canvas.sendToBack(frameObj);
        canvas.renderAll();
      });

      // İlk ürün
      if (project.products && project.products.length > 0) {
        loadProductImage(project.products[0].image, {
          pos_x: project.pos_x,
          pos_y: project.pos_y,
          width: project.width,
          height: project.height,
          radius: project.radius || 0,
        });
        renderThumbnails(project.products, project);
      }
    } catch (err) {
      console.error("Error fetching project details:", err);
    }
  }

  // --- 2) Thumbnail’ler
  function renderThumbnails(products, project) {
    thumbnailsList.innerHTML = "";
    products.forEach((p) => {
      const img = document.createElement("img");
      img.src = p.image;
      img.addEventListener("click", () =>
        loadProductImage(p.image, {
          pos_x: project.pos_x,
          pos_y: project.pos_y,
          width: project.width,
          height: project.height,
          radius: project.radius || 0,
        })
      );
      thumbnailsList.appendChild(img);
    });
  }

  // --- 3) Ürün görselini yükle
  function loadProductImage(url, coords = null) {
    if (productObj) canvas.remove(productObj);

    fabric.Image.fromURL(url, (img) => {
      productObj = img;
      productObj.originX = "left";
      productObj.originY = "top";

      if (coords && coords.width && coords.height && frameObj) {
        const { frameTLx, frameTLy } = getFrameMetrics();

        productObj.left = frameTLx + coords.pos_x;
        productObj.top = frameTLy + coords.pos_y;
        productObj.scaleX = coords.width / img.width;
        productObj.scaleY = coords.height / img.height;
      } else {
        productObj.left = canvas.getWidth() / 2;
        productObj.top = canvas.getHeight() / 2;
        productObj.scaleToWidth(200);
      }

      productObj.cornerColor = "blue";
      productObj.cornerStyle = "circle";
      productObj.objectCaching = false;

      canvas.add(productObj);
      canvas.setActiveObject(productObj);
      canvas.renderAll();

      syncInputs();
      updateClipPath();
    });
  }

  // --- 4) Input → Canvas
  function applyCoords() {
    if (!productObj || !frameObj) return;

    const { frameTLx, frameTLy } = getFrameMetrics();

    const x = parseInt(posX.value);
    const y = parseInt(posY.value);
    const w = parseInt(width.value);
    const h = parseInt(height.value);

    if (!Number.isNaN(x)) productObj.left = frameTLx + x;
    if (!Number.isNaN(y)) productObj.top = frameTLy + y;
    if (!Number.isNaN(w)) productObj.scaleX = w / productObj.width;
    if (!Number.isNaN(h)) productObj.scaleY = h / productObj.height;

    updateClipPath();
    canvas.renderAll();
  }

  // --- 4.1) Radius (önizleme düzeltildi)
  function updateClipPath() {
    if (!productObj) return;
  
    const r = parseFloat(radiusInput.value) || 0;
  
    // clipPath nesnenin kendi local koordinat sistemine göre tanımlanmalı
    const clip = new fabric.Rect({
      width: productObj.width,      // unscaled
      height: productObj.height,    // unscaled
      rx: r,
      ry: r,
      originX: "center",
      originY: "center",
    });
  
    // önemli nokta: clipPath productObj ile aynı şekilde scale edilecek
    clip.absolutePositioned = false;
    productObj.clipPath = clip;
  
    canvas.requestRenderAll();
  }
  
  [posX, posY, width, height].forEach((el) => el?.addEventListener("input", applyCoords));
  radiusInput?.addEventListener("input", updateClipPath);

  // --- Frame içi koordinatlar inputlara yazılır
  function syncInputs() {
    if (!productObj || !frameObj) return;

    const { frameTLx, frameTLy } = getFrameMetrics();

    const relLeft = productObj.left - frameTLx;
    const relTop = productObj.top - frameTLy;

    posX.value = Math.round(relLeft);
    posY.value = Math.round(relTop);
    width.value = Math.round(productObj.getScaledWidth());
    height.value = Math.round(productObj.getScaledHeight());
  }

  canvas.on("object:modified", () => {
    syncInputs();
    updateClipPath();
  });
  canvas.on("object:scaling", () => {
    syncInputs();
    updateClipPath();
  });

  // --- 5) Kaydet
  saveCoordsBtn.addEventListener("click", async () => {
    if (!productObj || !frameObj) return;

    const { frameTLx, frameTLy } = getFrameMetrics();

    const relLeft = productObj.left - frameTLx;
    const relTop = productObj.top - frameTLy;

    const coords = {
      pos_x: Math.round(relLeft),
      pos_y: Math.round(relTop),
      width: Math.round(productObj.getScaledWidth()),
      height: Math.round(productObj.getScaledHeight()),
      radius: parseInt(radiusInput.value) || 0,
    };

    console.log("[SAVE DEBUG] coords=", coords);

    try {
      const res = await fetch(`${API_BASE}/projects/${projectId}/coords`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(coords),
      });
      if (!res.ok) {
        alert("Coords save failed!");
        console.error(await res.text());
        return;
      }
      alert("Coords saved successfully!");
    } catch (err) {
      console.error("Error saving coords:", err);
    }
  });

  // --- 6) İşleme başlat
  startProcessingBtn.addEventListener("click", async () => {
    if (!productObj || !frameObj) return;

    const { frameTLx, frameTLy, kx, ky } = getFrameMetrics();

    const relLeft = productObj.left - frameTLx;
    const relTop = productObj.top - frameTLy;

    const coords = {
      pos_x: Math.round(relLeft * kx),
      pos_y: Math.round(relTop * ky),
      width: Math.round(productObj.getScaledWidth() * kx),
      height: Math.round(productObj.getScaledHeight() * ky),
      radius: parseInt(radiusInput.value) || 0,
    };

    console.log("[PROCESS DEBUG] coords=", coords);

    try {
      const saveRes = await fetch(`${API_BASE}/projects/${projectId}/coords`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(coords),
      });

      if (!saveRes.ok) {
        alert("Coords save failed!");
        console.error(await saveRes.text());
        return;
      }

      const res = await fetch(`${API_BASE}/processor/${projectId}/process`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(coords),
      });

      if (!res.ok) {
        alert("Processing failed!");
        console.error(await res.text());
        return;
      }

      const result = await res.json();
      alert("Processing started! Task ID: " + result.task_id);
      console.log("Task started:", result);
    } catch (err) {
      console.error("Error starting process:", err);
    }
  });

  fetchProjectDetails();
});
