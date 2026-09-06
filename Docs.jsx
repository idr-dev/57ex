export default function Docs() {
  return (
    <div className="shell docs">
      <h1>Setup guide</h1>
      <p className="sub">
        Everything you need to route trades through your key, from your first
        quote to wiring it into a bot or an exchange front-end.
      </p>

      <h2>1. Get a key</h2>
      <p>Connect a wallet on the homepage and sign the login message — that's the only credential you need. Generate a key from the dashboard and copy it somewhere safe; it's shown in full only once per reveal.</p>

      <h2>2. Point requests at the gateway, not at 0x directly</h2>
      <p>
        57eX mirrors 0x's Swap API request shape. Send the same query
        parameters you'd send to 0x, to 57eX's <code>/v1/</code> path instead,
        with your key in the <code>x-api-key</code> header. Don't send your 0x
        key from the client — 57eX attaches its own server-side.
      </p>
      <pre>{`curl "https://your-gateway.example.com/v1/swap/allowance-holder/quote?\\
chainId=8453&sellToken=USDC&buyToken=WETH&sellAmount=5000000000&taker=0xYourWallet" \\
  -H "x-api-key: 57ex_live_yourkeyhere"`}</pre>

      <h2>3. Get a price, then a firm quote</h2>
      <table>
        <thead><tr><th>Endpoint</th><th>Use it for</th></tr></thead>
        <tbody>
          <tr><td className="mono">/v1/swap/allowance-holder/price</td><td>Indicative pricing — no on-chain allowance needed, good for polling in a bot loop.</td></tr>
          <tr><td className="mono">/v1/swap/allowance-holder/quote</td><td>A firm, executable quote with transaction data your wallet/taker signs.</td></tr>
          <tr><td className="mono">/v1/swap/permit2/quote</td><td>Same, using Permit2 signatures instead of on-chain approvals.</td></tr>
        </tbody>
      </table>
      <p>Every response passes through unchanged from 0x except that the trade is already priced with your 15bps fee baked in — nothing extra to calculate on your end.</p>

      <h2>4. Wire it into an algo trading bot</h2>
      <pre>{`import requests

GATEWAY = "https://your-gateway.example.com"
API_KEY = "57ex_live_yourkeyhere"

def get_quote(sell_token, buy_token, sell_amount, taker, chain_id=8453):
    resp = requests.get(
        f"{GATEWAY}/v1/swap/allowance-holder/quote",
        params={
            "chainId": chain_id,
            "sellToken": sell_token,
            "buyToken": buy_token,
            "sellAmount": sell_amount,
            "taker": taker,
        },
        headers={"x-api-key": API_KEY},
    )
    resp.raise_for_status()
    return resp.json()

# quote["transaction"] holds the calldata your signer sends on-chain.
quote = get_quote("USDC", "WETH", "5000000000", "0xYourTakerWallet")`}</pre>
      <p>Sign and broadcast <code>quote["transaction"]</code> the same way you would with a raw 0x integration — 57eX doesn't change settlement, only pricing and fee attribution.</p>

      <h2>5. Wire it into your own exchange front-end</h2>
      <p>
        Use one shared key across your app's backend, and charge your users
        whatever spread makes sense on your side — the 15bps only covers what
        you pay upstream. A common pattern: quote through 57eX server-side,
        show the user an all-in price, and let your own margin be the
        difference between what 57eX returns and what you display.
      </p>
      <pre>{`const res = await fetch(
  \`\${GATEWAY}/v1/swap/allowance-holder/price?chainId=1&sellToken=\${sellToken}&buyToken=\${buyToken}&sellAmount=\${amount}\`,
  { headers: { "x-api-key": API_KEY } }
);
const price = await res.json();`}</pre>

      <h2>6. Check what you've earned</h2>
      <p>
        Each key's usage endpoint totals the fee amounts 0x reported back to
        57eX, grouped by the token the fee was paid in — that's the same data
        landing in your fee wallet on-chain, so it doubles as a running
        reconciliation.
      </p>
      <pre>{`GET /keys/{key_id}/usage
Authorization: Bearer <your dashboard session token>`}</pre>

      <h2>7. Run your own gateway (operators)</h2>
      <p>
        If you're standing this whole service up yourself rather than using
        someone else's deployment: set <code>ZEROX_API_KEY</code> to your 0x
        dashboard key and <code>FEE_RECIPIENT_ADDRESS</code> to the wallet
        that should receive the 15bps. Full instructions are in the
        project's README, including how to swap SQLite for Postgres and where
        to change the fee rate.
      </p>
    </div>
  );
}
