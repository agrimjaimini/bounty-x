import React, { useState } from 'react';
import { User } from '../types/api';
import { userApi } from '../services/api';
import { 
  TrophyIcon,
  CheckCircleIcon,
  CurrencyDollarIcon,
  StarIcon,
  BanknotesIcon,
  ClockIcon,
  PlusIcon
} from '@heroicons/react/24/outline';

interface UserStatsProps {
  user: User;
}

const UserStats: React.FC<UserStatsProps> = ({ user }) => {
  const [funding, setFunding] = useState(false);
  const [fundMessage, setFundMessage] = useState('');

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleFundWallet = async () => {
    try {
      setFunding(true);
      setFundMessage('');
      
      const result = await userApi.fundWallet(user.id);
      
      setFundMessage(`Successfully funded! New balance: ${result.balance_xrp} XRP`);
      
      // Refresh the page to update the user data after a short delay
      setTimeout(() => {
        window.location.reload();
      }, 2000);
      
    } catch (error: any) {
      console.error('Error funding wallet:', error);
      
      // Handle different types of errors
      if (error.response) {
        const status = error.response.status;
        const detail = error.response.data?.detail || 'Unknown error';
        
        switch (status) {
          case 400:
            setFundMessage(`Invalid request: ${detail}`);
            break;
          case 404:
            setFundMessage('User not found. Please log in again.');
            break;
          case 503:
            setFundMessage('Testnet faucet is currently unavailable. Please try again later.');
            break;
          case 500:
            setFundMessage('Server error. Please try again later.');
            break;
          default:
            setFundMessage(`Error: ${detail}`);
        }
      } else if (error.request) {
        setFundMessage('Network error. Please check your connection and try again.');
      } else {
        setFundMessage('An unexpected error occurred. Please try again.');
      }
    } finally {
      setFunding(false);
    }
  };

  return (
    <div className="space-y-6">
      
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
          
          <div className="mt-6 pt-6 border-t border-success-500/20">
            <button
              onClick={handleFundWallet}
              disabled={funding}
              className="w-full bg-gradient-to-r from-primary-500 to-accent-500 hover:from-primary-600 hover:to-accent-600 disabled:from-gray-600 disabled:to-gray-700 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-200 transform hover:scale-105 disabled:scale-100 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {funding ? (
                <>
                  <div className="spinner h-4 w-4"></div>
                  <span>Funding...</span>
                </>
              ) : (
                <>
                  <PlusIcon className="h-4 w-4" />
                  <span>Add Testnet Funds</span>
                </>
              )}
            </button>
            
            {fundMessage && (
              <div className={`mt-3 text-sm font-medium ${
                fundMessage.includes('Successfully') 
                  ? 'text-success-400' 
                  : 'text-error-400'
              }`}>
                {fundMessage}
              </div>
            )}
            
            <div className="mt-3 text-xs text-gray-500 text-center">
              Get testnet XRP to create and fund bounties
            </div>
          </div>
        </div>
      </div>

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