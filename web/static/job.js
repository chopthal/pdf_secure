const jobId = window.PDF_SECURE_JOB_ID;
let outputFilename = "output.pdf";
let polling = true;

function showError(message) {
  const err = document.getElementById("job-error");
  err.textContent = message;
  err.hidden = false;
}

function showDownloadButton() {
  const container = document.getElementById("download-actions");
  if (!container || container.dataset.ready === "1") return;
  container.dataset.ready = "1";

  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "btn-primary";
  btn.textContent = "다운로드";
  btn.addEventListener("click", downloadResult);
  container.appendChild(btn);
}

async function downloadResult() {
  const btn = document.querySelector("#download-actions .btn-primary");
  if (btn) {
    btn.disabled = true;
    btn.textContent = "다운로드 중...";
  }

  try {
    const res = await fetch(`/api/jobs/${jobId}/download`);
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      const detail = data.detail;
      const message =
        typeof detail === "string"
          ? detail
          : "아직 다운로드할 수 없습니다. 처리가 끝날 때까지 기다려 주세요.";
      showError(message);
      if (btn) {
        btn.disabled = false;
        btn.textContent = "다운로드";
      }
      return;
    }

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = outputFilename || "output.pdf";
    link.click();
    URL.revokeObjectURL(url);
  } catch {
    showError("다운로드 중 오류가 발생했습니다.");
  }

  if (btn) {
    btn.disabled = false;
    btn.textContent = "다운로드";
  }
}

async function poll() {
  if (!polling) return;

  try {
    const res = await fetch(`/api/jobs/${jobId}`);
    if (!res.ok) {
      setTimeout(poll, 1000);
      return;
    }
    const data = await res.json();

    document.getElementById("status-message").textContent =
      data.message || data.status;
    document.getElementById("progress-fill").style.width = `${data.progress || 0}%`;
    document.getElementById("progress-text").textContent = `${data.progress || 0}%`;

    if (data.status === "done") {
      polling = false;
      outputFilename = data.output_filename || outputFilename;
      showDownloadButton();
      return;
    }
    if (data.status === "failed") {
      polling = false;
      showError(data.error || "처리 실패");
      return;
    }
  } catch {
    /* 네트워크 일시 오류 — 폴링 유지 */
  }

  setTimeout(poll, 1000);
}

poll();
