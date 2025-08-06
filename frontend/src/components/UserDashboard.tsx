import React from 'react';
import { User } from '../types/api';
import { 
  TrophyIcon,
  CheckCircleIcon,
  CurrencyDollarIcon,
  StarIcon,
  BanknotesIcon
} from '@heroicons/react/24/outline';

interface UserDashboardProps {
  user: User;
}

const UserDashboard: React.FC<UserDashboardProps> = ({ user }) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold gradient-text mb-2">
              Welcome back, {user.username}!
            </h2>
            <p className="text-gray-400">
              Your last activity was {formatDate(user.last_updated)}
            </p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-success-400">
              {user.current_xrp_balance} XRP
            </div>
            <div className="text-sm text-gray-400">Current Balance</div>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card text-center">
          <div className="flex items-center justify-center mb-3">
            <div className="h-10 w-10 rounded-full bg-primary-500/20 flex items-center justify-center">
              <TrophyIcon className="h-5 w-5 text-primary-400" />
            </div>
          </div>
          <div className="text-2xl font-bold text-primary-400 mb-1">
            {user.bounties_created}
          </div>
          <div className="text-sm text-gray-400">Created</div>
        </div>
        
        <div className="card text-center">
          <div className="flex items-center justify-center mb-3">
            <div className="h-10 w-10 rounded-full bg-success-500/20 flex items-center justify-center">
              <CheckCircleIcon className="h-5 w-5 text-success-400" />
            </div>
          </div>
          <div className="text-2xl font-bold text-success-400 mb-1">
            {user.bounties_accepted}
          </div>
          <div className="text-sm text-gray-400">Accepted</div>
        </div>
        
        <div className="card text-center">
          <div className="flex items-center justify-center mb-3">
            <div className="h-10 w-10 rounded-full bg-warning-500/20 flex items-center justify-center">
              <CurrencyDollarIcon className="h-5 w-5 text-warning-400" />
            </div>
          </div>
          <div className="text-2xl font-bold text-warning-400 mb-1">
            {user.total_xrp_funded}
          </div>
          <div className="text-sm text-gray-400">Funded (XRP)</div>
        </div>
        
        <div className="card text-center">
          <div className="flex items-center justify-center mb-3">
            <div className="h-10 w-10 rounded-full bg-accent-500/20 flex items-center justify-center">
              <StarIcon className="h-5 w-5 text-accent-400" />
            </div>
          </div>
          <div className="text-2xl font-bold text-accent-400 mb-1">
            {user.total_xrp_earned}
          </div>
          <div className="text-sm text-gray-400">Earned (XRP)</div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <div className="flex items-center space-x-3 mb-4">
            <div className="h-8 w-8 rounded-full bg-primary-500/20 flex items-center justify-center">
              <TrophyIcon className="h-4 w-4 text-primary-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-200">Create New Bounty</h3>
          </div>
          <p className="text-gray-400 mb-4">
            Fund a new bounty to get help with your open source project
          </p>
          <a
            href="/create-bounty"
            className="btn btn-primary w-full"
          >
            Create Bounty
          </a>
        </div>

        <div className="card">
          <div className="flex items-center space-x-3 mb-4">
            <div className="h-8 w-8 rounded-full bg-success-500/20 flex items-center justify-center">
              <BanknotesIcon className="h-4 w-4 text-success-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-200">View Profile</h3>
          </div>
          <p className="text-gray-400 mb-4">
            See your detailed statistics and bounty history
          </p>
          <a
            href="/profile"
            className="btn btn-secondary w-full"
          >
            View Profile
          </a>
        </div>
      </div>
    </div>
  );
};

export default UserDashboard; 