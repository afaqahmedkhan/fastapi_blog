export function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text ?? "";
  return div.innerHTML;
}

export function formatDate(isoString) {
  return new Date(isoString).toLocaleDateString(undefined, {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

export function getErrorMessage(error) {
  if (!error) return "Something went wrong.";
  if (typeof error.detail === "string") return error.detail;
  if (Array.isArray(error.detail)) {
    return error.detail.map((item) => item.msg ?? String(item)).join(", ");
  }
  return "Something went wrong.";
}
