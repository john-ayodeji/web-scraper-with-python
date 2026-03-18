const statusDot = document.getElementById("statusDot");
const statusText = document.getElementById("statusText");
const metricPages = document.getElementById("metricPages");
const metricInternal = document.getElementById("metricInternal");
const metricExternal = document.getElementById("metricExternal");
const metricLastRun = document.getElementById("metricLastRun");
const errorText = document.getElementById("errorText");
const graphImage = document.getElementById("graphImage");
const jsonPreview = document.getElementById("jsonPreview");
const imageGrid = document.getElementById("imageGrid");
const saveBtn = document.getElementById("saveBtn");
const runBtn = document.getElementById("runBtn");

const form = document.getElementById("settingsForm");
let pollingTimer = null;
let socket = null;

function setRunning(running) {
  statusDot.classList.remove("running", "idle");
  statusDot.classList.add(running ? "running" : "idle");
  statusText.textContent = running ? "Running" : "Idle";
  runBtn.disabled = running;
  runBtn.textContent = running ? "Running..." : "Run Now";
}

function fillSettings(settings) {
  Object.keys(settings).forEach((key) => {
    const el = document.getElementById(key);
    if (!el) {
      return;
    }
    if (el.type === "checkbox") {
      el.checked = Boolean(settings[key]);
    } else {
      el.value = settings[key] ?? "";
    }
  });
}

function formPayload() {
  return {
    url: document.getElementById("url").value,
    max_concurrency: Number(document.getElementById("max_concurrency").value),
    max_pages: Number(document.getElementById("max_pages").value),
    interval_minutes: Number(document.getElementById("interval_minutes").value),
    request_timeout: Number(document.getElementById("request_timeout").value),
    max_retries: Number(document.getElementById("max_retries").value),
    resend_api_key: document.getElementById("resend_api_key").value,
    email_to: document.getElementById("email_to").value,
    resend_from: document.getElementById("resend_from").value,
    send_email: document.getElementById("send_email").checked,
    report_filename: "report.json",
    graph_filename: "report_graph.png",
  };
}

async function fetchSettings() {
  const res = await fetch("/api/settings");
  if (!res.ok) {
    throw new Error("Failed to load settings");
  }
  const settings = await res.json();
  fillSettings(settings);
}

function renderMetrics(status) {
  const summary = status.summary || {};
  metricPages.textContent = summary.pages ?? 0;
  metricInternal.textContent = summary.internal_links ?? 0;
  metricExternal.textContent = summary.external_links ?? 0;
  metricLastRun.textContent = status.last_run_at || "never";
  errorText.textContent = status.last_error || "";
  setRunning(Boolean(status.running));
}

async function fetchStatus() {
  const res = await fetch("/api/status");
  if (!res.ok) {
    throw new Error("Failed to load status");
  }
  const status = await res.json();
  renderMetrics(status);
}

function renderImageGrid(reportData) {
  imageGrid.innerHTML = "";
  const imageUrls = [];
  reportData.forEach((page) => {
    (page.image_urls || []).forEach((url) => imageUrls.push(url));
  });

  imageUrls.slice(0, 12).forEach((url) => {
    const img = document.createElement("img");
    img.src = url;
    img.loading = "lazy";
    img.alt = "Discovered image";
    img.addEventListener("error", () => {
      img.remove();
    });
    imageGrid.appendChild(img);
  });

  if (imageGrid.children.length === 0) {
    imageGrid.textContent = "No image URLs found in current report.";
  }
}

async function fetchReport() {
  const res = await fetch("/api/report-json");
  if (!res.ok) {
    jsonPreview.textContent = "No report yet.";
    imageGrid.textContent = "No image URLs found in current report.";
    return;
  }
  const data = await res.json();
  jsonPreview.textContent = JSON.stringify(data.slice(0, 12), null, 2);
  renderImageGrid(data);
  graphImage.src = `/api/report-graph?t=${Date.now()}`;
}

async function saveSettings(event) {
  event.preventDefault();
  saveBtn.disabled = true;
  saveBtn.textContent = "Saving...";
  try {
    const payload = formPayload();
    const res = await fetch("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.detail || "Failed to save settings");
    }
    await fetchStatus();
  } catch (error) {
    errorText.textContent = String(error.message || error);
  } finally {
    saveBtn.disabled = false;
    saveBtn.textContent = "Save Settings";
  }
}

async function runNow() {
  runBtn.disabled = true;
  runBtn.textContent = "Starting...";
  try {
    const res = await fetch("/api/run-now", { method: "POST" });
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.detail || "Failed to start crawl");
    }
  } catch (error) {
    errorText.textContent = String(error.message || error);
    setRunning(false);
  }
}

function startStatusSocket() {
  const wsProto = location.protocol === "https:" ? "wss" : "ws";
  socket = new WebSocket(`${wsProto}://${location.host}/ws/status`);
  socket.onerror = () => {
    startPollingFallback();
  };
  socket.onmessage = (event) => {
    const status = JSON.parse(event.data);
    renderMetrics(status);
    if (!status.running) {
      fetchReport().catch(() => {});
    }
  };

  socket.onclose = () => {
    startPollingFallback();
    setTimeout(startStatusSocket, 2000);
  };
}

function startPollingFallback() {
  if (pollingTimer !== null) {
    return;
  }
  pollingTimer = setInterval(() => {
    fetchStatus().catch(() => {});
    fetchReport().catch(() => {});
  }, 3000);
}

form.addEventListener("submit", saveSettings);
runBtn.addEventListener("click", runNow);

Promise.all([fetchSettings(), fetchStatus(), fetchReport()]).catch((error) => {
  errorText.textContent = String(error.message || error);
});
startStatusSocket();
