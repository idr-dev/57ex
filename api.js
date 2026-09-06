const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ? JSON.stringify(body.detail) : `Request failed (${res.status})`);
  }
  return res.status === 204 ? null : res.json();
}

export const api = {
  getNonce: (address) => request(`/auth/nonce?address=${address}`),
  verify: (address, message, signature) =>
    request("/auth/verify", { method: "POST", body: JSON.stringify({ address, message, signature }) }),
  listKeys: (token) => request("/keys", { headers: { Authorization: `Bearer ${token}` } }),
  createKey: (token, label) =>
    request("/keys", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: JSON.stringify({ label }),
    }),
  revokeKey: (token, id) =>
    request(`/keys/${id}`, { method: "DELETE", headers: { Authorization: `Bearer ${token}` } }),
  keyUsage: (token, id) => request(`/keys/${id}/usage`, { headers: { Authorization: `Bearer ${token}` } }),
};

export { API_BASE };
