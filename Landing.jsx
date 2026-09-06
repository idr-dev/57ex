export default function Landing({ onConnect, connecting, error, goDocs }) {
  return (
    <>
      <section className="hero">
        <div>
          <h1>Give algo traders a swap API in one click, take 15bps for keeping the lights on.</h1>
          <p className="lede">
            57eX sits between your users and 0x's liquidity. Every trade that
            comes through the API you issue routes through your 0x account, and
            a 0.15% fee lands in your wallet automatically at settlement — no
            invoicing, no custody, no separate fee contract.
          </p>
          <div className="hero-actions">
            <button className="btn btn-primary" onClick={onConnect} disabled={connecting}>
              {connecting ? "Confirm in wallet…" : "Connect wallet & get a key"}
            </button>
            <button className="btn" onClick={goDocs}>Read the setup guide</button>
          </div>
          {error && <p className="hero-note" style={{ color: "var(--bad)" }}>{error}</p>}
          <p className="hero-note">No email, no password — sign in by signing a message with your wallet.</p>
        </div>

        <div className="ticket">
          <div className="ticket-head">
            <span><span className="ticket-dot" />quote · chainId=8453</span>
            <span>allowance-holder/quote</span>
          </div>
          <div className="ticket-body">{`{
  `}<span className="k">sellToken</span>: <span className="v">"USDC"</span>{`,
  `}<span className="k">buyToken</span>: <span className="v">"WETH"</span>{`,
  `}<span className="k">sellAmount</span>: <span className="v">"5000000000"</span>{`,
  `}<span className="k">swapFeeRecipient</span>: <span className="v">"0xYourWallet"</span>{`,
  `}<span className="fee-line">swapFeeBps: 15</span>{`
}`}</div>
          <div className="ticket-foot">
            <span className="label">Fee earned on this trade</span>
            <span className="amt">$0.75 → your wallet</span>
          </div>
        </div>
      </section>

      <section className="block">
        <h2>Built for people shipping trading infrastructure</h2>
        <p className="sub">
          Whether you're running a bot desk or standing up your own exchange
          front-end, 57eX gives you a metered, revenue-generating swap
          endpoint without writing routing or settlement logic yourself.
        </p>
        <div className="spec-grid">
          <div className="spec-cell">
            <h3>Algo trading desks</h3>
            <p>Point your strategy at one endpoint across every chain 0x supports, and get billed in the token you're already trading.</p>
          </div>
          <div className="spec-cell">
            <h3>Exchange builders</h3>
            <p>Use the same key across your whole front-end. The 15bps spread is your take rate — raise it, or split it further downstream.</p>
          </div>
          <div className="spec-cell">
            <h3>Anyone tired of AMM plumbing</h3>
            <p>0x already aggregates the liquidity and handles settlement. 57eX just meters access and takes a cut on your behalf.</p>
          </div>
        </div>
      </section>

      <section className="block">
        <h2>How a trade actually moves</h2>
        <p className="sub">Four steps, none of which touch your users' funds — 0x settles the swap directly to the taker's wallet.</p>
        <div className="flow">
          <div className="flow-row">
            <span className="flow-idx">01</span>
            <div>
              <h4>Your bot calls 57eX</h4>
              <p>Same request shape as 0x's Swap API — sellToken, buyToken, sellAmount, chainId — sent with your 57eX API key.</p>
            </div>
          </div>
          <div className="flow-row">
            <span className="flow-idx">02</span>
            <div>
              <h4>57eX adds the fee and your 0x credentials</h4>
              <p>swapFeeRecipient and swapFeeBps=15 are attached server-side. Your 0x API key never reaches the client.</p>
            </div>
          </div>
          <div className="flow-row">
            <span className="flow-idx">03</span>
            <div>
              <h4>0x prices and settles the trade</h4>
              <p>0x aggregates liquidity across sources, returns a quote, and settles on-chain when the taker signs.</p>
            </div>
          </div>
          <div className="flow-row">
            <span className="flow-idx">04</span>
            <div>
              <h4>Your fee lands automatically</h4>
              <p>15bps of the trade is sent to your wallet at settlement. 57eX logs the amount so your dashboard stays accurate.</p>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
