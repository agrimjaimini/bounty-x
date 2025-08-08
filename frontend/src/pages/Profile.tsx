import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { bountyApi } from '../services/api';
import { Bounty } from '../types/api';
import UserStats from '../components/UserStats';
import { 
  UserCircleIcon,
  CurrencyDollarIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  WalletIcon
} from '@heroicons/react/24/outline';
import { TrashIcon } from '@heroicons/react/24/solid';
import { SkeletonText, SkeletonCircle } from '../components/ui/Skeleton';

const Profile: React.FC = () => {
  const { user } = useAuth();
  const [userBounties, setUserBounties] = useState<Bounty[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [cancelingId, setCancelingId] = useState<number | null>(null);

  useEffect(() => {
    if (user) {
      fetchUserBounties();
    }
  }, [user]);

  const fetchUserBounties = async () => {
    try {
      setLoading(true);
      const bounties = await bountyApi.getBountiesByFunder(user!.id);
      setUserBounties(bounties);
    } catch (error) {
      setError('Failed to load user bounties');
      console.error('Error fetching user bounties:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'open':
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-success-500/20 text-success-400 border border-success-500/30">
            <CheckCircleIcon className="h-3 w-3 mr-1" />
            Open
          </span>
        );
      case 'accepted':
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-warning-500/20 text-warning-400 border border-warning-500/30">
            <ClockIcon className="h-3 w-3 mr-1" />
            In Progress
          </span>
        );
      case 'claimed':
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-primary-500/20 text-primary-400 border border-primary-500/30">
            <CurrencyDollarIcon className="h-3 w-3 mr-1" />
            Completed
          </span>
        );
      default:
        return null;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const formatBountyName = (name: string) => {
    return name
      .replace(/_/g, ' ')
      .replace(/-/g, ' ')
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
  };

  const handleCancel = async (bountyId: number) => {
    try {
      setCancelingId(bountyId);
      await bountyApi.cancelBounty(bountyId);
      await fetchUserBounties();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to cancel bounty');
    } finally {
      setCancelingId(null);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        <div className="card">
          <div className="flex items-center space-x-6">
            <SkeletonCircle className="h-20 w-20" />
            <div className="flex-1">
              <SkeletonText className="h-7 w-48 mb-2" />
              <SkeletonText className="h-4 w-80" />
            </div>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="card-compact">
              <SkeletonCircle className="h-12 w-12 mb-4" />
              <SkeletonText className="h-7 w-16 mb-2" />
              <SkeletonText className="h-4 w-24" />
            </div>
          ))}
        </div>
        <div className="card">
          <SkeletonText className="h-6 w-48 mb-6" />
          <div className="space-y-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <SkeletonText key={i} className="h-10 w-full" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div className="card">
        <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-4 sm:space-y-0 sm:space-x-6">
          <div className="relative">
            <div className="h-20 w-20 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center">
              <UserCircleIcon className="h-12 w-12 text-white" />
            </div>
            <div className="absolute -bottom-1 -right-1 h-6 w-6 bg-success-500 rounded-full border-2 border-dark-900"></div>
          </div>
          <div className="flex-1 min-w-0">
            <h1 className="text-3xl font-bold gradient-text mb-2">{user?.username}</h1>
            <div className="flex items-center space-x-4 text-gray-400">
              <div className="flex items-center space-x-2">
                <WalletIcon className="h-4 w-4" />
                <span className="font-mono text-sm break-all">{user?.xrp_address}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {error && (
        <div className="error-message">
          <ExclamationTriangleIcon className="h-5 w-5 mr-2" />
          {error}
        </div>
      )}

      {user && <UserStats user={user} />}

      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold gradient-text">Your Bounties</h2>
          <div className="text-sm text-gray-400">
            {userBounties.length} bounty{userBounties.length !== 1 ? 'ies' : ''}
          </div>
        </div>
        
        {userBounties.length === 0 ? (
          <div className="text-center py-12">
            <div className="h-24 w-24 rounded-full bg-dark-800/50 flex items-center justify-center mx-auto mb-6">
              <CurrencyDollarIcon className="h-12 w-12 text-gray-500" />
            </div>
            <h3 className="text-xl font-semibold text-gray-300 mb-3">No bounties yet</h3>
            <p className="text-gray-500 max-w-md mx-auto">
              Create your first bounty to start building the future of open source development!
            </p>
          </div>
        ) : (
          <div className="table-dark overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                      Bounty
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                      Amount
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                      Created
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {userBounties.map((bounty) => (
                    <tr key={bounty.id} className="hover:bg-neutral-900/40 transition-colors duration-200">
                      <td className="px-6 py-4">
                        <div>
                          <div className="text-sm font-semibold text-neutral-200 mb-1">
                            {formatBountyName(bounty.bounty_name)}
                          </div>
                          <div className="text-sm text-neutral-500 truncate max-w-xs">
                            {bounty.github_issue_url}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm font-semibold text-warning-400">
                          {bounty.amount} XRP
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        {getStatusBadge(bounty.status)}
                      </td>
                      <td className="px-6 py-4 text-sm text-neutral-400">
                        {formatDate(bounty.created_at)}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <a href={`/bounties/${bounty.id}`} className="text-primary-400 hover:text-primary-300 font-medium transition-colors duration-200">
                            View Details →
                          </a>
                          {bounty.status === 'open' && (
                            <button
                              onClick={() => handleCancel(bounty.id)}
                              className="btn-danger btn-xs inline-flex items-center gap-1"
                              disabled={cancelingId === bounty.id}
                            >
                              {cancelingId === bounty.id ? 'Cancelling...' : (
                                <>
                                  <TrashIcon className="h-3 w-3" />
                                  Cancel
                                </>
                              )}
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      <div className="card">
        <div className="flex items-center space-x-3 mb-6">
          <div className="h-8 w-8 rounded-full bg-primary-500/20 flex items-center justify-center">
            <WalletIcon className="h-4 w-4 text-primary-400" />
          </div>
          <h2 className="text-2xl font-bold gradient-text">Wallet Information</h2>
        </div>
        
        <div className="bg-dark-800/50 rounded-xl p-6 border border-dark-700/50">
          <div className="space-y-4">
            <div>
              <label className="form-label">XRP Address</label>
              <div className="bg-dark-900/50 rounded-lg p-3 border border-dark-600/50">
                <p className="font-mono text-sm text-gray-300 break-all">{user?.xrp_address}</p>
              </div>
            </div>
            <div className="flex items-start space-x-3 p-4 bg-primary-500/10 rounded-lg border border-primary-500/20">
              <div className="h-5 w-5 rounded-full bg-primary-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                <div className="h-2 w-2 rounded-full bg-primary-400"></div>
              </div>
              <div className="text-sm text-gray-300">
                <p className="font-medium mb-1">Testnet Wallet</p>
                <p>This is your testnet wallet address. Use it to receive payments from completed bounties.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile; 