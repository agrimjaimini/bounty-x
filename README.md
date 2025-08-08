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
API runs on `http://localhost:8000`

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

## Contributing

Fork, make changes, test, and submit a PR. We welcome contributions!

## License

MIT License - feel free to use and modify.
