# Bounty-X Frontend

A modern, responsive React frontend for the Bounty-X decentralized bounty platform. Built with TypeScript, Tailwind CSS, and React Router.

## Features

- **Modern UI/UX**: Clean, responsive design with Tailwind CSS
- **Authentication**: User registration and login with XRP wallet integration
- **Bounty Management**: Create, browse, accept, and claim bounties
- **Real-time Updates**: Live status updates and statistics
- **Mobile Responsive**: Works seamlessly on all devices
- **TypeScript**: Full type safety throughout the application

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **React Router** - Navigation
- **Axios** - HTTP client
- **Heroicons** - Icons
- **Headless UI** - Accessible components

## Getting Started

### Prerequisites

- Node.js 16+ 
- npm or yarn
- Backend API running on `http://localhost:8000`

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The application will be available at `http://localhost:3000`.

### Building for Production

```bash
npm run build
```

This creates an optimized production build in the `build` folder.

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Navbar.tsx      # Navigation component
│   └── ProtectedRoute.tsx # Route protection
├── contexts/           # React contexts
│   └── AuthContext.tsx # Authentication state
├── pages/              # Page components
│   ├── Home.tsx        # Landing page
│   ├── Login.tsx       # Login page
│   ├── Register.tsx    # Registration page
│   ├── Bounties.tsx    # Bounty listing
│   ├── CreateBounty.tsx # Create bounty form
│   ├── BountyDetail.tsx # Bounty details
│   └── Profile.tsx     # User profile
├── services/           # API services
│   └── api.ts          # API client
├── types/              # TypeScript interfaces
│   └── api.ts          # API types
├── App.tsx             # Main app component
└── index.tsx           # Entry point
```

## API Integration

The frontend communicates with the Bounty-X backend API running on port 8000. Key endpoints include:

- **Authentication**: `/register`, `/login`
- **Bounties**: `/bounties/`, `/bounties/{id}`, `/bounties/search/`
- **User Management**: `/users/{id}`, `/users/{id}/statistics`

## Key Features

### Authentication
- User registration with automatic XRP testnet wallet creation
- Secure login with session management
- Protected routes for authenticated users

### Bounty Management
- **Create Bounties**: Fund GitHub issues with XRP
- **Browse Bounties**: Search and filter by status
- **Accept Bounties**: Developers can accept open bounties
- **Claim Bounties**: Submit merge requests to claim rewards

### User Experience
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Live status changes and statistics
- **Error Handling**: Comprehensive error messages and loading states
- **Accessibility**: WCAG compliant components

## Styling

The application uses Tailwind CSS with custom components:

- **Buttons**: `.btn-primary`, `.btn-secondary`, `.btn-success`, `.btn-warning`
- **Cards**: `.card` for content containers
- **Forms**: `.input-field` for form inputs
- **Colors**: Custom primary, success, and warning color schemes

## Development

### Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

### Code Style

- TypeScript strict mode enabled
- ESLint configuration for code quality
- Prettier for code formatting
- Component-based architecture

## Deployment

The frontend can be deployed to any static hosting service:

1. Build the application: `npm run build`
2. Deploy the `build` folder to your hosting service
3. Configure your hosting service to serve `index.html` for all routes (SPA routing)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of the Bounty-X platform.
