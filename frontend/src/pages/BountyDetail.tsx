import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { bountyApi } from '../services/api';
import { Bounty } from '../types/api';
import { 
  CurrencyDollarIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ArrowLeftIcon,
  UserIcon,
  LinkIcon
} from '@heroicons/react/24/outline';

const BountyDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [bounty, setBounty] = useState<Bounty | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAcceptForm, setShowAcceptForm] = useState(false);
  const [showClaimForm, setShowClaimForm] = useState(false);
  const [acceptForm, setAcceptForm] = useState({
    developer_address: '',
    finish_after: '86400',
  });
  const [claimForm, setClaimForm] = useState({
    merge_request_url: '',
  });
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    if (id) {
      fetchBounty();
    }
  }, [id]);

  const fetchBounty = async () => {
    try {
      setLoading(true);
      const data = await bountyApi.getBounty(parseInt(id!));
      setBounty(data);
    } catch (error) {
      setError('Failed to load bounty details');
      console.error('Error fetching bounty:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptBounty = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionLoading(true);
    setError('');

    try {
      await bountyApi.acceptBounty(parseInt(id!), {
        developer_address: acceptForm.developer_address,
        finish_after: parseInt(acceptForm.finish_after),
      });
      
      setShowAcceptForm(false);
      fetchBounty(); // Refresh bounty data
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to accept bounty');
    } finally {
      setActionLoading(false);
    }
  };

  const handleClaimBounty = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionLoading(true);
    setError('');

    try {
      await bountyApi.claimBounty(parseInt(id!), {
        merge_request_url: claimForm.merge_request_url,
      });
      
      setShowClaimForm(false);
      fetchBounty(); // Refresh bounty data
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to claim bounty');
    } finally {
      setActionLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'open':
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-success-500/20 text-success-400 border border-success-500/30">
            <CheckCircleIcon className="h-4 w-4 mr-1" />
            Open
          </span>
        );
      case 'accepted':
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-warning-500/20 text-warning-400 border border-warning-500/30">
            <ClockIcon className="h-4 w-4 mr-1" />
            In Progress
          </span>
        );
      case 'claimed':
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-primary-500/20 text-primary-400 border border-primary-500/30">
            <CurrencyDollarIcon className="h-4 w-4 mr-1" />
            Completed
          </span>
        );
      case 'cancelled':
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-500/20 text-red-400 border border-red-500/30">
            <ExclamationTriangleIcon className="h-4 w-4 mr-1" />
            Cancelled
          </span>
        );
      default:
        return null;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!bounty) {
    return (
      <div className="text-center py-12">
        <ExclamationTriangleIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-white mb-2">Bounty not found</h3>
        <p className="text-gray-400">The bounty you're looking for doesn't exist.</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate('/bounties')}
          className="flex items-center text-gray-400 hover:text-white transition-colors"
        >
          <ArrowLeftIcon className="h-5 w-5 mr-1" />
          Back to Bounties
        </button>
        {getStatusBadge(bounty.status)}
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-3 rounded-lg flex items-center">
          <ExclamationTriangleIcon className="h-5 w-5 mr-2" />
          {error}
        </div>
      )}

      {/* Bounty Details */}
      <div className="card">
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">
              {bounty.bounty_name}
            </h1>
            <div className="flex items-center text-gray-300">
              <CurrencyDollarIcon className="h-5 w-5 mr-1" />
              <span className="text-xl font-semibold text-warning-400">{bounty.amount} XRP</span>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold text-white mb-3">Details</h3>
              <div className="space-y-3">
                <div>
                  <label className="text-sm font-medium text-gray-400">GitHub Issue</label>
                  <div className="flex items-center mt-1">
                    <LinkIcon className="h-4 w-4 text-gray-400 mr-2" />
                    <a
                      href={bounty.github_issue_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary-400 hover:text-primary-300 truncate"
                    >
                      {bounty.github_issue_url}
                    </a>
                  </div>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-gray-400">Funder Address</label>
                  <div className="flex items-center mt-1">
                    <UserIcon className="h-4 w-4 text-gray-400 mr-2" />
                    <span className="font-mono text-sm text-gray-300">
                      {bounty.funder_address.slice(0, 8)}...{bounty.funder_address.slice(-8)}
                    </span>
                  </div>
                </div>

                {bounty.developer_address && (
                  <div>
                    <label className="text-sm font-medium text-gray-400">Developer Address</label>
                    <div className="flex items-center mt-1">
                      <UserIcon className="h-4 w-4 text-gray-400 mr-2" />
                      <span className="font-mono text-sm text-gray-300">
                        {bounty.developer_address.slice(0, 8)}...{bounty.developer_address.slice(-8)}
                      </span>
                    </div>
                  </div>
                )}

                <div>
                  <label className="text-sm font-medium text-gray-400">Created</label>
                  <p className="mt-1 text-gray-300">{formatDate(bounty.created_at)}</p>
                </div>

                <div>
                  <label className="text-sm font-medium text-gray-400">Last Updated</label>
                  <p className="mt-1 text-gray-300">{formatDate(bounty.updated_at)}</p>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-white mb-3">Escrow Information</h3>
              <div className="space-y-3">
                {bounty.escrow_id ? (
                  <>
                    <div>
                      <label className="text-sm font-medium text-gray-400">Escrow ID</label>
                      <p className="mt-1 font-mono text-sm break-all text-gray-300">{bounty.escrow_id}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-400">Escrow Sequence</label>
                      <p className="mt-1 text-gray-300">{bounty.escrow_sequence}</p>
                    </div>
                  </>
                ) : (
                  <p className="text-gray-500">No escrow created yet</p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      {user && (
        <div className="card">
          <h3 className="text-lg font-semibold text-white mb-4">Actions</h3>
          
          {bounty.status === 'open' && user.id !== bounty.funder_id && (
            <button
              onClick={() => setShowAcceptForm(true)}
              className="btn-success"
            >
              Accept Bounty
            </button>
          )}

          {bounty.status === 'accepted' && bounty.developer_address && (
            <button
              onClick={() => setShowClaimForm(true)}
              className="btn-warning"
            >
              Claim Bounty
            </button>
          )}
        </div>
      )}

      {/* Accept Bounty Modal */}
      {showAcceptForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-dark-800 rounded-lg p-6 max-w-md w-full border border-dark-700">
            <h3 className="text-lg font-semibold text-white mb-4">Accept Bounty</h3>
            <form onSubmit={handleAcceptBounty} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Your XRP Address
                </label>
                <input
                  type="text"
                  required
                  value={acceptForm.developer_address}
                  onChange={(e) => setAcceptForm({...acceptForm, developer_address: e.target.value})}
                  className="input-field"
                  placeholder="Enter your XRP address"
                />
              </div>

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowAcceptForm(false)}
                  className="btn-secondary flex-1"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={actionLoading}
                  className="btn-success flex-1"
                >
                  {actionLoading ? 'Accepting...' : 'Accept'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Claim Bounty Modal */}
      {showClaimForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-dark-800 rounded-lg p-6 max-w-md w-full border border-dark-700">
            <h3 className="text-lg font-semibold text-white mb-4">Claim Bounty</h3>
            <form onSubmit={handleClaimBounty} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Merge Request URL
                </label>
                <input
                  type="url"
                  required
                  value={claimForm.merge_request_url}
                  onChange={(e) => setClaimForm({...claimForm, merge_request_url: e.target.value})}
                  className="input-field"
                  placeholder="https://github.com/username/repo/pull/123"
                />
              </div>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowClaimForm(false)}
                  className="btn-secondary flex-1"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={actionLoading}
                  className="btn-warning flex-1"
                >
                  {actionLoading ? 'Claiming...' : 'Claim'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default BountyDetail; 