# XRPL Testnet Feature Bounty Portal

A web portal for posting, funding, and claiming bounties on open-source GitHub issues using XRPL Testnet XRP.

## Features
- Post a bounty for a GitHub issue/PR with Testnet XRP escrow
- Boost existing bounties by adding more funds
- Claim bounties after PR merge and verification
- Multisig escrow release by maintainers
- Dispute and review flow for merged PRs
- Secure wallet interactions (Xumm, xrpl.js)

## Tech Stack
- **Frontend:** React, xrpl.js
- **Backend:** Node.js, PostgreSQL, GitHub OAuth, webhooks
- **XRPL Testnet:** wss://s.altnet.rippletest.net:51233

## Getting Started
- Use the Testnet faucet to fund new accounts during onboarding
- See `/frontend` and `/backend` for setup instructions 