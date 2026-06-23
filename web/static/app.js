function updatePreview() {
  const name = document.getElementById("buyer_name")?.value.trim() || "";
  const phone = document.getElementById("buyer_phone")?.value.trim() || "";
  const el = document.getElementById("watermark-preview");
  if (!el) return;
  if (name && phone) {
    el.textContent = `이 책은 ${name} (${phone}) 님이 구매하신 전자책입니다.`;
  } else if (name || phone) {
    el.textContent = `이 책은 ${name || ""} (${phone || ""}) 님이 구매하신 전자책입니다.`;
  } else {
    el.textContent = "이름과 연락처를 입력하세요.";
  }
}

document.getElementById("buyer_name")?.addEventListener("input", updatePreview);
document.getElementById("buyer_phone")?.addEventListener("input", updatePreview);

const PDF_PASSWORD_PATTERN = /^[ -~]+$/;
const PDF_PASSWORD_MESSAGE =
  "PDF 비밀번호는 영문, 숫자, 기본 특수문자만 사용할 수 있습니다. (한글 불가)";

function validatePdfPassword(password) {
  if (!password.trim()) return "PDF 비밀번호를 입력해주세요.";
  if (!PDF_PASSWORD_PATTERN.test(password)) return PDF_PASSWORD_MESSAGE;
  return null;
}

document.getElementById("job-form")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.target;
  const errorEl = document.getElementById("form-error");
  const submitBtn = document.getElementById("submit-btn");
  errorEl.hidden = true;
  submitBtn.disabled = true;

  const password = form.pdf_password?.value ?? "";
  const passwordError = validatePdfPassword(password);
  if (passwordError) {
    errorEl.textContent = passwordError;
    errorEl.hidden = false;
    submitBtn.disabled = false;
    return;
  }

  const body = new FormData(form);
  try {
    const res = await fetch("/api/jobs", { method: "POST", body });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(data.detail || "요청 실패");
    }
    window.location.href = `/jobs/${data.job_id}`;
  } catch (err) {
    errorEl.textContent = err.message;
    errorEl.hidden = false;
    submitBtn.disabled = false;
  }
});
