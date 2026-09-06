import { useEffect, useState } from "react";
import { api } from "../lib/api";

function short(addr) {
  return addr ? `${addr.slice(0, 6)}…${addr.slice(-4)}` : "";
}

export default function Dashboard({ address, token }) {
  const [keys, setKeys] = useState([]);
  const [label, setLabel] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [revealedId, setRevealedId] = useState(null);

  async function refresh() {
    try {
      setLoading(true);
      const data = await api.listKeys(token);
      setKeys(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { refresh(); }, []); // eslint-disable-line

  async function handleCreate(e) {
    e.preventDefault();
    try {
      const created = await api.createKey(token, label || "default");
      setLabel("");
      setKeys((prev) => [...prev, created]);
      setRevealedId(created.id);
    } catch (e) {
      setError(e.message);
    }
  }

  async function handleRevoke(id) {
    try {
      await api.revokeKey(token, id);
      setKeys((prev) => prev.map((k) => (k.id === id ? { ...k, active: false } : k)));
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <div className="shell">
      <div className="dash-header">
        <h1>Your API keys</h1>
        <span className="wallet-chip">{short(address)}</span>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <form className="form-row" onSubmit={handleCreate}>
        <input
          placeholder="Label this key, e.g. 'mainnet-bot-1'"
          value={label}
          onChange={(e) => setLabel(e.target.value)}
        />
        <button className="btn btn-primary" type="submit">Generate key</button>
      </form>

      {loading ? (
        <p style={{ color: "var(--text-muted)" }}>Loading…</p>
      ) : keys.length === 0 ? (
        <div className="empty-state">No keys yet. Generate one above to start routing trades.</div>
      ) : (
        keys.map((k) => (
          <div className="key-row" key={k.id}>
            <div>
              <div className="key-label">{k.label}</div>
              <div className="key-value">{revealedId === k.id ? k.key : `${k.key.slice(0, 12)}${"•".repeat(20)}`}</div>
            </div>
            <button className="btn" onClick={() => setRevealedId(revealedId === k.id ? null : k.id)}>
              {revealedId === k.id ? "Hide" : "Reveal"}
            </button>
            {k.active ? (
              <>
                <span className="status active">active</span>
                <button className="btn" onClick={() => handleRevoke(k.id)}>Revoke</button>
              </>
            ) : (
              <span className="status revoked">revoked</span>
            )}
          </div>
        ))
      )}
    </div>
  );
}
