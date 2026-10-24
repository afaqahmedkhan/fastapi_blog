export function getToken() {
  return localStorage.getItem("token");
}

export async function getCurrentUser() {
  const token = getToken();
  if (!token) return null;
  return null;
}
