# Bounty-X: XRPL Testnet Feature Bounty Portal

A decentralized bounty platform for posting, funding, and claiming bounties on open-source GitHub issues using XRPL Testnet XRP.

## Features

### Backend (FastAPI)
- Post a bounty for a GitHub issue/PR with Testnet XRP escrow
- Boost existing bounties by adding more funds
- Claim bounties after PR merge and verification
- Multisig escrow release by maintainers
- Conditional escrow with time-based completion
- GitHub integration for issue verification

### Frontend (React + TypeScript)
- Modern, responsive web interface
- User authentication with XRP wallet integration
- Real-time bounty browsing and management
- Interactive bounty creation and claiming
- User profiles with statistics
- Mobile-responsive design

## Project Structure

```
bounty-x/
├── backend/           # FastAPI backend
│   ├── main.py       # API endpoints
│   ├── db.py         # Database operations
│   ├── utils.py      # XRPL utilities
│   └── README.md     # Backend documentation
├── frontend/         # React frontend
│   ├── src/          # Source code
│   ├── public/       # Static assets
│   └── README.md     # Frontend documentation
├── requirements.txt  # Python dependencies
└── README.md        # This file
```

## Quick Start

### Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Start the backend server:
```bash
cd backend
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Install Node.js dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## API Documentation

The backend provides a RESTful API with the following key endpoints:

- `POST /register` - User registration
- `POST /login` - User authentication
- `POST /bounties/` - Create new bounty
- `GET /bounties/` - List all bounties
- `POST /bounties/{id}/accept` - Accept a bounty
- `POST /bounties/{id}/claim` - Claim a completed bounty

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLite** - Database
- **XRPL** - XRP Ledger integration
- **Pydantic** - Data validation

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **React Router** - Navigation
- **Axios** - HTTP client

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test both backend and frontend
5. Submit a pull request

## License

This project is open source and available under the MIT License.
