import { useState } from "react";
import Landing from "./pages/Landing.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Docs from "./pages/Docs.jsx";
import { signInWithEthereum } from "./lib/wallet.js";

function short(addr) {
  return addr ? `${addr.slice(0, 6)}…${addr.slice(-4)}` : "";
}

export default function App() {
  const [view, setView] = useState("landing"); // landing | dashboard | docs
  const [session, setSession] = useState(null); // { address, token }
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState("");

  async function handleConnect() {
    setError("");
    setConnecting(true);
    try {
      const { address, token } = await signInWithEthereum();
      setSession({ address, token });
      setView("dashboard");
    } catch (e) {
      setError(e.message || "Could not connect wallet.");
    } finally {
      setConnecting(false);
    }
  }

  return (
    <div>
      <nav className="nav">
        <div className="shell nav-inner">
          <div className="brand" onClick={() => setView("landing")} style={{ cursor: "pointer" }}>
            <span className="brand-mark">57eX</span> · swap gateway
          </div>
          <div className="nav-links">
            <button className="linklike" onClick={() => setView("docs")}>Docs</button>
            {session ? (
              <>
                <button className="linklike" onClick={() => setView("dashboard")}>Dashboard</button>
                <span className="pill">{short(session.address)}</span>
              </>
            ) : (
              <button className="btn btn-primary" onClick={handleConnect} disabled={connecting}>
                {connecting ? "Confirm in wallet…" : "Connect wallet"}
              </button>
            )}
          </div>
        </div>
      </nav>

      {view === "landing" && (
        <div className="shell">
          <Landing onConnect={handleConnect} connecting={connecting} error={error} goDocs={() => setView("docs")} />
        </div>
      )}

      {view === "dashboard" && session && <Dashboard address={session.address} token={session.token} />}
      {view === "dashboard" && !session && (
        <div className="shell" style={{ padding: "60px 0" }}>
          <p>Connect your wallet first.</p>
        </div>
      )}

      {view === "docs" && <Docs />}

      <footer className="site-footer">
        <div className="shell">57eX is a self-hosted gateway you deploy and configure — see the Docs for operator setup.</div>
      </footer>
    </div>
  );
}
