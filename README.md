# Bounty-X

A decentralized bounty platform that connects open-source developers with funders using XRP on the XRPL testnet. Post bounties for GitHub issues, fund them with testnet XRP, and claim rewards when work is completed.

Created in collaboration with Ripple as part of the XRPL Student Builder Residency.

## What it does

- **Post bounties** for GitHub issues with XRP escrow
- **Fund existing bounties** to increase rewards
- **Claim bounties** after PR merge and verification
- **Time-based escrow** that auto-releases or cancels
- **GitHub integration** for seamless issue tracking

## Getting started

### Backend
```bash
pip install -r requirements.txt
cd backend
python main.py
```
API runs on `http://localhost:8000` (endpoints are served under `/api`)

### Frontend
```bash
cd frontend
npm install
npm start
```
App runs on `http://localhost:3000`

## How it works

1. **Create a bounty** - Fund a GitHub issue with testnet XRP
2. **Accept a bounty** - Developers claim and work on issues
3. **Submit work** - Create a PR with the bounty reference
4. **Claim reward** - Get paid when PR is merged

## Tech stack

**Backend:** FastAPI, SQLite, XRPL  
**Frontend:** React, TypeScript, Tailwind CSS

## Basic architecture

- **Frontend**: React/TS UI. Axios client targets `.../api` (set `REACT_APP_API_BASE_URL`).
- **Backend**: FastAPI + SQLite. CORS enabled; XRPL/GitHub helpers in `backend/utils/`.
- **Tables**: `users`, `bounties`, `bounty_contributions`.
- **Lifecycle**: Create/Boost (DB only) → Accept (escrows per contribution; mark `accepted`) → Claim (verify PR + developer key; finish escrows; credit dev) → Cancel (open only).

## XRPL integration

- **Network**: XRPL Testnet JSON-RPC (`https://s.altnet.rippletest.net:51234/`).
- **Wallets**: Create/fund via faucet; balances via `AccountInfo`; validate reserves (≥ 20 XRP) and amount+fee before escrows.
- **Escrows**: On accept, generate preimage condition; `EscrowCreate` per contribution with shared condition and `CancelAfter` from `time_limit_seconds` (10m–30d).
- **Claim**: Verify merged PR references the issue and includes developer key; finish escrows with stored fulfillment/condition to release XRP to the developer.

## Contributing

Fork, make changes, test, and submit a PR. We welcome contributions!

## License

MIT License - feel free to use and modify.
