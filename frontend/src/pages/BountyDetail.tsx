import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { SkeletonText } from '../components/ui/Skeleton';
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
import { TrashIcon } from '@heroicons/react/24/solid';
 

const BountyDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [bounty, setBounty] = useState<Bounty | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAcceptForm, setShowAcceptForm] = useState(false);
  const [showBoostForm, setShowBoostForm] = useState(false);
  const [showClaimForm, setShowClaimForm] = useState(false);
  const [showCancelConfirm, setShowCancelConfirm] = useState(false);
  const [acceptForm, setAcceptForm] = useState({
    developer_address: '',
  });
  const [claimForm, setClaimForm] = useState({
    merge_request_url: '',
  });
  const [developerSecretKey, setDeveloperSecretKey] = useState<string>('');
  const [actionLoading, setActionLoading] = useState(false);
  const [boostAmount, setBoostAmount] = useState<string>('');
  const [contributions, setContributions] = useState<Array<{ id: number; bounty_id: number; contributor_id: number; contributor_address: string; amount: number; escrow_id?: string | null; escrow_sequence?: number | null; created_at: string; updated_at: string; }>>([]);

  const fetchBounty = useCallback(async () => {
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
  }, [id]);

  useEffect(() => {
    if (id) {
      fetchBounty();
    }
  }, [id, fetchBounty]);

  useEffect(() => {
    const fetchContribs = async () => {
      try {
        if (!id) return;
        const list = await bountyApi.getContributions(parseInt(id));
        setContributions(Array.isArray(list) ? list : []);
      } catch (e) {}
    };
    fetchContribs();
  }, [id, showBoostForm, showAcceptForm, bounty?.status]);

  useEffect(() => {
    const fetchDevKeyIfAuthorized = async () => {
      if (!bounty || !user) return;
      if (bounty.developer_address && user.xrp_address === bounty.developer_address) {
        try {
          const resp = await bountyApi.getDeveloperSecret(bounty.id, user.id);
          if (resp?.developer_secret_key) {
            setDeveloperSecretKey(resp.developer_secret_key);
          }
        } catch (e) {
          // silently ignore forbidden/not found
        }
      }
    };
    fetchDevKeyIfAuthorized();
  }, [bounty, user]);

  const handleAcceptBounty = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionLoading(true);
    setError('');

    try {
      const response = await bountyApi.acceptBounty(parseInt(id!), {
        developer_address: acceptForm.developer_address,
      });
      
      // Store the developer secret key
      if (response.developer_secret_key) {
        setDeveloperSecretKey(response.developer_secret_key);
      }
      
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

  const handleCancelBounty = async () => {
    setActionLoading(true);
    setError('');
    try {
      await bountyApi.cancelBounty(parseInt(id!));
      setShowCancelConfirm(false);
      navigate('/bounties');
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to cancel bounty');
    } finally {
      setActionLoading(false);
    }
  };

  const handleBoostBounty = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;
    setActionLoading(true);
    setError('');
    try {
      const amount = parseFloat(boostAmount);
      if (isNaN(amount) || amount <= 0) {
        setError('Enter a valid amount');
        return;
      }
      await bountyApi.boostBounty(parseInt(id!), user.id, amount);
      setShowBoostForm(false);
      setBoostAmount('');
      fetchBounty();
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to boost bounty');
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

  const extractRepoName = (githubUrl: string) => {
    const match = githubUrl.match(/github\.com\/([^/]+\/[^/]+)/);
    return match ? match[1] : 'Repository';
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

  const hasAvailableActions = () => {
    if (!user || !bounty || bounty.status === 'claimed' || bounty.status === 'cancelled') {
      return false;
    }
    
    const canAccept = bounty.status === 'open' && user.id !== bounty.funder_id;
    const canCancel = bounty.status === 'open' && user.id === bounty.funder_id;
    
    const canClaim = bounty.status === 'accepted' && 
                     bounty.developer_address && 
                     user.xrp_address === bounty.developer_address;
    
    return canAccept || canCancel || canClaim;
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="card">
          <div className="space-y-4">
            <SkeletonText className="h-7 w-2/3" />
            <SkeletonText className="h-5 w-40" />
            <SkeletonText className="h-4 w-full" />
            <SkeletonText className="h-4 w-5/6" />
          </div>
        </div>
        <div className="grid md:grid-cols-2 gap-6">
          <div className="card">
            <SkeletonText className="h-5 w-32 mb-4" />
            <div className="space-y-3">
              <SkeletonText className="h-4 w-3/4" />
              <SkeletonText className="h-4 w-1/2" />
              <SkeletonText className="h-4 w-2/3" />
              <SkeletonText className="h-4 w-1/3" />
            </div>
          </div>
          <div className="card">
            <SkeletonText className="h-5 w-40 mb-4" />
            <div className="space-y-3">
              <SkeletonText className="h-4 w-2/3" />
              <SkeletonText className="h-4 w-1/2" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!bounty) {
    return (
      <motion.div 
        className="text-center py-12"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, ease: "easeOut" }}
      >
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: "spring", stiffness: 300, damping: 20 }}
        >
          <ExclamationTriangleIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        </motion.div>
        <motion.h3 
          className="text-lg font-medium text-white mb-2"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          Bounty not found
        </motion.h3>
        <motion.p 
          className="text-gray-400"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          The bounty you're looking for doesn't exist.
        </motion.p>
      </motion.div>
    );
  }

  return (
      <motion.div 
      className="max-w-4xl mx-auto space-y-6"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      layout
    >
      <motion.div 
        className="flex items-center justify-between"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1, duration: 0.3, ease: "easeOut" }}
      >
        <motion.button
          onClick={() => navigate('/bounties')}
          className="flex items-center text-gray-400 hover:text-white transition-colors"
          whileHover={{ x: -3 }}
          whileTap={{ scale: 0.98 }}
          transition={{ type: "spring", stiffness: 400, damping: 25 }}
        >
          <ArrowLeftIcon className="h-5 w-5 mr-1" />
          Back to Bounties
        </motion.button>
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: "spring", stiffness: 300, damping: 20 }}
        >
          {getStatusBadge(bounty.status)}
        </motion.div>
      </motion.div>

        <div className="text-sm text-neutral-400">
          <a href="/bounties" className="hover:text-neutral-200">Bounties</a>
          <span className="mx-2">/</span>
          <a href={bounty.github_issue_url} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">
            {extractRepoName(bounty.github_issue_url)}
          </a>
          <span className="mx-2">/</span>
          <span className="text-neutral-300">Issue #{bounty.id}</span>
        </div>

      <AnimatePresence mode="wait">
        {error && (
          <motion.div 
            key="error-message"
            className="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-3 rounded-lg flex items-center"
            initial={{ opacity: 0, y: -10, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.98 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
          >
            <ExclamationTriangleIcon className="h-5 w-5 mr-2" />
            {error}
          </motion.div>
        )}
      </AnimatePresence>

      <motion.div 
        key="bounty-details"
        className="card"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.3, ease: "easeOut" }}
        whileHover={{ y: -1 }}
        layout
      >
        <div className="space-y-6">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            <motion.h1 
              className="text-3xl font-bold gradient-text text-balance mb-2"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4, duration: 0.3, ease: "easeOut" }}
            >
              {bounty.bounty_name}
            </motion.h1>
            <motion.div 
              className="flex items-center text-gray-300"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5, duration: 0.3, ease: "easeOut" }}
            >
              <CurrencyDollarIcon className="h-5 w-5 mr-1 text-neutral-400" />
              <span className="text-xl font-semibold text-warning-400">{bounty.amount} XRP</span>
              {contributions.filter(c => !!c.escrow_id).length > 0 && (
                <span className="ml-3 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-success-500/20 text-success-400 border border-success-500/30">
                  <CheckCircleIcon className="h-4 w-4 mr-1 text-neutral-400" />
                  {contributions.filter(c => !!c.escrow_id).length} Escrow{contributions.filter(c => !!c.escrow_id).length > 1 ? 's' : ''} Created
                </span>
              )}
            </motion.div>
            
            {bounty.description && (
              <motion.div 
                className="mt-4"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6, duration: 0.3, ease: "easeOut" }}
              >
                <h3 className="text-lg font-semibold text-white mb-2">Description</h3>
                <p className="text-gray-300 leading-relaxed whitespace-pre-wrap">
                  {bounty.description}
                </p>
              </motion.div>
            )}
          </motion.div>

          <div className="grid md:grid-cols-2 gap-6">
            <div className="card-gradient p-5 rounded-2xl">
              <h3 className="text-lg font-semibold gradient-text mb-3">Details</h3>
              <div className="space-y-3">
                <div>
                  <label className="text-sm font-medium text-gray-400">GitHub Issue</label>
                  <div className="flex items-center mt-1">
                    <LinkIcon className="h-4 w-4 text-primary-400 mr-2" />
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
                
                {/* Contributors removed from Details per request; shown only under Escrow Information */}

                {bounty.developer_address && (
                  <div>
                    <label className="text-sm font-medium text-gray-400">Developer Address</label>
                    <div className="flex items-center mt-1 gap-2">
                      <UserIcon className="h-4 w-4 text-gray-400 mr-2" />
                      <span className="font-mono text-sm text-gray-300">{bounty.developer_address.slice(0, 8)}...{bounty.developer_address.slice(-8)}</span>
                      <button
                        onClick={() => navigator.clipboard.writeText(bounty.developer_address!)}
                        className="text-xs text-primary-400 hover:text-primary-300"
                      >
                        Copy
                      </button>
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

            <div className="card-gradient p-5 rounded-2xl">
              <h3 className="text-lg font-semibold gradient-text mb-3">Escrow Information</h3>
              {contributions && contributions.filter(c => !!c.escrow_id).length > 0 ? (
                <div className="grid grid-cols-1 gap-4">
                  {contributions.filter(c => !!c.escrow_id).map((c) => (
                    <div key={c.id} className="card-compact card-gradient p-6">
                      <div className="flex items-start justify-between gap-4">
                        <div className="min-w-0">
                          <div className="text-xs text-gray-400">Contributor</div>
                          <div className="font-mono text-sm text-gray-300">{c.contributor_address.slice(0,12)}...{c.contributor_address.slice(-12)}</div>
                        </div>
                        <div className="text-sm text-warning-400 font-semibold flex-shrink-0 whitespace-nowrap">{c.amount} XRP</div>
                      </div>
                      <div className="mt-4 space-y-3">
                        <div className="min-w-0">
                          <div className="text-xs text-gray-400">Escrow ID</div>
                          <div className="flex items-center gap-2">
                            <div
                              title={c.escrow_id || undefined}
                              className="font-mono text-sm text-gray-300 flex-1 min-w-0 break-all leading-snug"
                              style={{ display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}
                            >
                              {c.escrow_id || '—'}
                            </div>
                            {c.escrow_id && (
                              <button
                                onClick={() => navigator.clipboard.writeText(c.escrow_id!)}
                                className="text-xs text-primary-400 hover:text-primary-300 flex-shrink-0"
                              >
                                Copy
                              </button>
                            )}
                          </div>
                        </div>
                        <div>
                          <div className="text-xs text-gray-400">Escrow Sequence</div>
                          <div className="font-mono text-sm text-gray-300">{c.escrow_sequence ?? '—'}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500">No escrows created yet</p>
              )}
            </div>
          </div>
        </div>
      </motion.div>

      <AnimatePresence mode="wait">
        {hasAvailableActions() && (
          <motion.div 
            key="action-buttons"
            className="card"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            transition={{ delay: 0.3, duration: 0.3, ease: "easeOut" }}
          >
            <h3 className="text-lg font-semibold text-white mb-4">Actions</h3>
            
            <div className="flex flex-wrap gap-3">
              {bounty.status === 'open' && user && user.id !== bounty.funder_id && (
                <motion.button
                  onClick={() => setShowAcceptForm(true)}
                  className="btn-success"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  transition={{ type: "spring", stiffness: 400, damping: 25 }}
                >
                  Accept Bounty
                </motion.button>
              )}

              {bounty.status === 'open' && user && user.id !== bounty.funder_id && (
                <motion.button
                  onClick={() => setShowBoostForm(true)}
                  className="btn-primary"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  transition={{ type: "spring", stiffness: 400, damping: 25 }}
                >
                  Boost Bounty
                </motion.button>
              )}

              {bounty.status === 'open' && user && user.id === bounty.funder_id && (
                <motion.button
                  onClick={() => setShowCancelConfirm(true)}
                  className="btn-danger inline-flex items-center gap-2"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  transition={{ type: "spring", stiffness: 400, damping: 25 }}
                >
                  <TrashIcon className="h-4 w-4" />
                  Cancel Bounty
                </motion.button>
              )}
            </div>

            {bounty.status === 'accepted' && bounty.developer_address && (
              <>
                {developerSecretKey && user && bounty.developer_address === user.xrp_address && (
                  <motion.div 
                    className="mb-4 p-4 bg-warning-500/10 border border-warning-500/20 rounded-lg"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1, duration: 0.3 }}
                  >
                    <h4 className="text-sm font-medium text-warning-400 mb-2">Developer Secret Key</h4>
                    <p className="text-xs text-gray-400 mb-2">
                      Include this secret key in your merge request to verify you completed this bounty:
                    </p>
                    <div className="flex items-center space-x-2">
                      <code className="text-sm bg-dark-700 px-2 py-1 rounded text-warning-300 font-mono break-all">
                        {developerSecretKey}
                      </code>
                      <button
                        onClick={() => navigator.clipboard.writeText(developerSecretKey)}
                        className="text-xs text-primary-400 hover:text-primary-300"
                      >
                        Copy
                      </button>
                    </div>
                  </motion.div>
                )}
                {user && user.xrp_address === bounty.developer_address && (
                  <motion.button
                    onClick={() => setShowClaimForm(true)}
                    className="btn-warning"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    transition={{ type: "spring", stiffness: 400, damping: 25 }}
                  >
                    Claim Bounty
                  </motion.button>
                )}
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>


      <AnimatePresence>
        {showBoostForm && (
          <motion.div 
            className="modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div 
              className="modal-content"
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              transition={{ type: "spring", stiffness: 400, damping: 30 }}
            >
            <h3 className="text-lg font-semibold text-white mb-4">Boost Bounty</h3>
            <form onSubmit={handleBoostBounty} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Amount (XRP)
                </label>
                <input
                  type="number"
                  min="0"
                  step="0.000001"
                  required
                  value={boostAmount}
                  onChange={(e) => setBoostAmount(e.target.value)}
                  className="input-field"
                  placeholder="Enter amount to add"
                />
              </div>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowBoostForm(false)}
                  className="btn-secondary flex-1"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={actionLoading}
                  className="btn-primary flex-1"
                >
                  {actionLoading ? 'Boosting...' : 'Boost'}
                </button>
              </div>
            </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
      <AnimatePresence>
        {showAcceptForm && (
          <motion.div 
            className="modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div 
              className="modal-content"
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              transition={{ type: "spring", stiffness: 400, damping: 30 }}
            >
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
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {showCancelConfirm && (
          <motion.div 
            className="modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div 
              className="modal-content"
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              transition={{ type: "spring", stiffness: 400, damping: 30 }}
            >
              <h3 className="text-lg font-semibold text-white mb-4">Cancel Bounty</h3>
              <p className="text-gray-300 mb-6">Are you sure you want to cancel this bounty? This action cannot be undone.</p>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowCancelConfirm(false)}
                  className="btn-secondary flex-1"
                >
                  Keep Open
                </button>
                <button
                  type="button"
                  disabled={actionLoading}
                  onClick={handleCancelBounty}
                  className="btn-danger flex-1"
                >
                  {actionLoading ? 'Cancelling...' : 'Confirm Cancel'}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {showClaimForm && (
          <motion.div 
            className="modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div 
              className="modal-content"
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              transition={{ type: "spring", stiffness: 400, damping: 30 }}
            >
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
              <div>
                <p className="text-sm text-gray-300 mb-1">
                  Make sure your merge request includes the developer secret key that was provided when you accepted this bounty.
                </p>
                <p className="text-xs text-gray-500">
                  The secret key should be included in your merge request title or description for verification.
                </p>
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
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default BountyDetail; 