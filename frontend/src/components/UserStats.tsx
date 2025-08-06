import React from 'react';
import { User } from '../types/api';
import { 
  TrophyIcon,
  CheckCircleIcon,
  CurrencyDollarIcon,
  StarIcon,
  BanknotesIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

interface UserStatsProps {
  user: User;
}

const UserStats: React.FC<UserStatsProps> = ({ user }) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getActivityLevel = () => {
    const totalBounties = user.bounties_created + user.bounties_accepted;
    if (totalBounties === 0) return { level: 'Newcomer', color: 'text-gray-400' };
    if (totalBounties < 5) return { level: 'Active', color: 'text-success-400' };
    if (totalBounties < 15) return { level: 'Experienced', color: 'text-warning-400' };
    return { level: 'Veteran', color: 'text-primary-400' };
  };

  const activityLevel = getActivityLevel();

  return (
    <div className="space-y-6">
      {/* Activity Level */}
      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-200 mb-1">Activity Level</h3>
            <p className="text-sm text-gray-400">Based on your bounty activity</p>
          </div>
          <div className={`text-2xl font-bold ${activityLevel.color}`}>
            {activityLevel.level}
          </div>
        </div>
      </div>

      {/* Statistics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card text-center group hover:scale-105 transition-transform duration-300">
          <div className="flex items-center justify-center mb-4">
            <div className="h-12 w-12 rounded-full bg-primary-500/20 flex items-center justify-center">
              <TrophyIcon className="h-6 w-6 text-primary-400" />
            </div>
          </div>
          <div className="text-3xl font-bold text-primary-400 mb-2">
            {user.bounties_created}
          </div>
          <div className="text-gray-400 font-medium">Bounties Created</div>
        </div>
        
        <div className="card text-center group hover:scale-105 transition-transform duration-300">
          <div className="flex items-center justify-center mb-4">
            <div className="h-12 w-12 rounded-full bg-success-500/20 flex items-center justify-center">
              <CheckCircleIcon className="h-6 w-6 text-success-400" />
            </div>
          </div>
          <div className="text-3xl font-bold text-success-400 mb-2">
            {user.bounties_accepted}
          </div>
          <div className="text-gray-400 font-medium">Bounties Accepted</div>
        </div>
        
        <div className="card text-center group hover:scale-105 transition-transform duration-300">
          <div className="flex items-center justify-center mb-4">
            <div className="h-12 w-12 rounded-full bg-warning-500/20 flex items-center justify-center">
              <CurrencyDollarIcon className="h-6 w-6 text-warning-400" />
            </div>
          </div>
          <div className="text-3xl font-bold text-warning-400 mb-2">
            {user.total_xrp_funded} XRP
          </div>
          <div className="text-gray-400 font-medium">Total Funded</div>
        </div>
        
        <div className="card text-center group hover:scale-105 transition-transform duration-300">
          <div className="flex items-center justify-center mb-4">
            <div className="h-12 w-12 rounded-full bg-accent-500/20 flex items-center justify-center">
              <StarIcon className="h-6 w-6 text-accent-400" />
            </div>
          </div>
          <div className="text-3xl font-bold text-accent-400 mb-2">
            {user.total_xrp_earned} XRP
          </div>
          <div className="text-gray-400 font-medium">Total Earned</div>
        </div>
      </div>

      {/* Current Balance */}
      <div className="card">
        <div className="flex items-center space-x-3 mb-6">
          <div className="h-8 w-8 rounded-full bg-success-500/20 flex items-center justify-center">
            <BanknotesIcon className="h-4 w-4 text-success-400" />
          </div>
          <h2 className="text-2xl font-bold gradient-text">Current Balance</h2>
        </div>
        
        <div className="bg-gradient-to-r from-success-500/10 to-accent-500/10 rounded-xl p-6 border border-success-500/20">
          <div className="text-center">
            <div className="text-5xl font-bold text-success-400 mb-2">
              {user.current_xrp_balance} XRP
            </div>
            <div className="text-gray-400 font-medium">Available Balance</div>
            <div className="text-sm text-gray-500 mt-2">
              Last updated: {formatDate(user.last_updated)}
            </div>
          </div>
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <div className="flex items-center space-x-3 mb-4">
            <div className="h-6 w-6 rounded-full bg-primary-500/20 flex items-center justify-center">
              <ClockIcon className="h-3 w-3 text-primary-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-200">Performance Metrics</h3>
          </div>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Total Activity</span>
              <span className="font-semibold text-gray-200">
                {user.bounties_created + user.bounties_accepted} bounties
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Success Rate</span>
              <span className="font-semibold text-gray-200">
                {user.bounties_created > 0 
                  ? Math.round((user.total_xrp_earned / user.total_xrp_funded) * 100) 
                  : 0}%
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Avg. Bounty Value</span>
              <span className="font-semibold text-gray-200">
                {user.bounties_created > 0 
                  ? (user.total_xrp_funded / user.bounties_created).toFixed(1) 
                  : 0} XRP
              </span>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center space-x-3 mb-4">
            <div className="h-6 w-6 rounded-full bg-accent-500/20 flex items-center justify-center">
              <StarIcon className="h-3 w-3 text-accent-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-200">Earnings Overview</h3>
          </div>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Total Invested</span>
              <span className="font-semibold text-warning-400">
                {user.total_xrp_funded} XRP
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Total Earned</span>
              <span className="font-semibold text-success-400">
                {user.total_xrp_earned} XRP
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Net Profit</span>
              <span className={`font-semibold ${
                user.total_xrp_earned - user.total_xrp_funded >= 0 
                  ? 'text-success-400' 
                  : 'text-error-400'
              }`}>
                {(user.total_xrp_earned - user.total_xrp_funded).toFixed(2)} XRP
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserStats; 