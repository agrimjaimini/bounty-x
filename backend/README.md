# Bounty System API

A FastAPI-based bounty system that integrates with XRPL (XRP Ledger) for escrow management and GitHub for issue tracking.

## Features

- **Automatic Escrow Creation**: When a bounty is created, an XRPL escrow is automatically created
- **GitHub Integration**: Bounties are linked to GitHub issues
- **Merge Request Verification**: Developers can claim bounties by submitting merge requests that reference the issue
- **XRPL Integration**: Uses XRPL testnet for escrow transactions

## API Endpoints

### Create Bounty
**POST** `/bounties/`

Creates a new bounty and automatically creates an XRPL escrow.

**Request Body:**
```json
{
  "github_issue_url": "https://github.com/example/repo/issues/123",
  "funder_address": "rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe",
  "funder_secret": "sEdTM1uX8pu2do5XvTnutH6HsouMaM2",
  "amount": 100.0,
  "finish_after": 86400
}
```

**Response:**
```json
{
  "id": 1,
  "github_issue_url": "https://github.com/example/repo/issues/123",
  "funder_address": "rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe",
  "developer_address": null,
  "amount": 100.0,
  "escrow_id": "ABC123...",
  "status": "funded",
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

### List Bounties
**GET** `/bounties/`

Returns all bounties in the system.

### Get Bounty
**GET** `/bounties/{bounty_id}`

Returns a specific bounty by ID.

### Claim Bounty
**POST** `/bounties/{bounty_id}/claim`

Allows a developer to claim a bounty by submitting a merge request URL.

**Request Body:**
```json
{
  "developer_address": "rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe",
  "merge_request_url": "https://github.com/example/repo/pull/456"
}
```

**Response:**
```json
{
  "message": "Bounty claimed successfully",
  "bounty_id": 1,
  "developer_address": "rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe",
  "merge_request_url": "https://github.com/example/repo/pull/456"
}
```

## Bounty Statuses

- `open`: Bounty created but escrow not yet funded
- `funded`: Escrow created and funded
- `claimed`: Developer has claimed the bounty
- `escrow_failed`: Escrow creation failed

## Merge Request Verification

The system verifies that merge requests contain references to the original issue number. It looks for patterns like:
- `#123`
- `closes #123`
- `fixes #123`
- `resolves #123`

## Setup and Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
uvicorn main:app --reload
```

3. Test the API:
```bash
python test_api.py
```

## Security Notes

⚠️ **Important**: This is a demo implementation. In production:

- Never store private keys/secrets in plain text
- Use secure key management systems
- Implement proper authentication and authorization
- Use HTTPS for all API communications
- Validate and sanitize all inputs
- Implement rate limiting

## XRPL Integration

The system uses XRPL testnet for escrow transactions. For production:

- Use XRPL mainnet
- Implement proper wallet management
- Add transaction monitoring
- Handle escrow completion and cancellation

## Database Schema

```sql
CREATE TABLE bounties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    github_issue_url TEXT NOT NULL,
    funder_address TEXT NOT NULL,
    developer_address TEXT,
    amount REAL NOT NULL,
    escrow_id TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
``` 