# 57eX — a fee-taking swap gateway on top of the 0x API

57eX lets people request an API key, then trade crypto through that key. Every
request gets forwarded to **your** 0x API account with a 15 bps (0.15%) fee
attached, which 0x pays straight to your wallet at settlement. You never
custody user funds — 0x settles trades directly to whoever signs them.

```
 user's bot / exchange          57eX (this project)              0x API
┌─────────────────┐   x-api-key   ┌──────────────────┐  0x-api-key  ┌─────────┐
│ GET /v1/swap/... │ ───────────► │ validate key       │ ───────────► │ price / │
│                  │               │ inject swapFeeBps  │              │ quote / │
│                  │ ◄─────────── │ + swapFeeRecipient │ ◄─────────── │ settle  │
└─────────────────┘   response    │ log usage          │   response   └─────────┘
                                   └──────────────────┘
```

## What's in here

```
backend/    FastAPI service: wallet login, API key management, the proxy itself
frontend/   React (Vite) site: landing page, wallet-connect dashboard, docs
```

## How the fee actually gets collected

0x's Swap API has built-in support for this — no custom smart contract
needed. On every `/quote` or `/price` call, 57eX adds:

| Parameter | Value | What it does |
|---|---|---|
| `swapFeeRecipient` | your wallet address | where the fee is paid |
| `swapFeeBps` | `15` | 0.15% of the trade |
| `swapFeeToken` | the trade's `buyToken` | which token the fee is paid in |

0x settles that fee to your wallet as part of the same on-chain transaction
the trade executes in. 57eX also reads back the exact fee amount from 0x's
response (`fees.integratorFee.amount`) and logs it, so the dashboard shows
real collected fees, not estimates.

## 1. Get a 0x API key

Sign up at [dashboard.0x.org](https://dashboard.0x.org) and create an API
key. This is the account every trade will actually route through, so its
rate limits and pricing tier apply to all of your users combined.

## 2. Run the backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:

```
ZEROX_API_KEY=your-0x-api-key
FEE_RECIPIENT_ADDRESS=0xYourWalletAddress
FEE_BPS=15
JWT_SECRET=<generate with: openssl rand -hex 32>
ALLOWED_ORIGINS=http://localhost:5173
```

Then start it:

```bash
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for interactive API docs (Swagger UI).

## 3. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`. Set `VITE_API_BASE_URL` in a `.env` file
there if your backend isn't on `localhost:8000`.

## 4. How a person uses the site

1. They open the site and click **Connect wallet**. This is Sign-In with
   Ethereum (EIP-4361) — no email or password. They sign a plain-text
   message; nothing is broadcast on-chain and it costs no gas.
2. From the dashboard, they click **Generate key** to get a key like
   `57ex_live_...`. Keys are shown in full only right after creation and
   behind a "Reveal" toggle after that.
3. They send trading requests to `https://your-domain/v1/<0x swap path>`
   with `x-api-key: <their key>` instead of calling `api.0x.org` directly.
   Every other parameter (`chainId`, `sellToken`, `buyToken`, `sellAmount`,
   `taker`, etc.) is identical to 0x's own Swap API — 57eX is a drop-in
   proxy, not a different API shape. All chains 0x supports work, since
   chain selection is just the `chainId` query parameter.
4. They can revoke a key any time from the dashboard, and check
   `/keys/{id}/usage` to see request counts and fees earned per token.

Full request/response examples (curl, Python, JS) are in the **Docs** page
of the site itself (`frontend/src/pages/Docs.jsx`).

## Deploying it for real

- **Backend**: any host that runs a Python/ASGI app (Fly.io, Render,
  Railway, a plain VPS behind nginx + systemd). Swap `DATABASE_URL` to a
  managed Postgres instance instead of SQLite once you have concurrent
  writers.
- **Frontend**: `npm run build` produces a static `dist/` folder — deploy it
  to Vercel, Netlify, Cloudflare Pages, or your backend's own static file
  serving.
- **HTTPS everywhere.** Wallet signing and bearer tokens should never travel
  over plain HTTP in production.
- **Rate limiting**: the included limiter is a config value only
  (`RATE_LIMIT_PER_MINUTE`) — wire up something like `slowapi` + Redis
  before opening this up publicly, so one key can't exhaust your 0x quota.
- **Key storage**: keys are stored in plaintext in this MVP so they can be
  "revealed" again from the dashboard. If you'd rather they're shown once
  and never retrievable again, hash them (like passwords) and compare hashes
  on each request instead.

## One more thing worth knowing

Running a service that takes a fee on other people's crypto trades can
touch money-transmission, securities, or licensing rules depending on your
jurisdiction and how the service is structured — this varies a lot by
country and even by state. Nothing here is legal advice; it's worth a
conversation with a lawyer familiar with crypto/fintech regulation in the
jurisdictions your users are in before you take this live.
