import React, { useMemo, useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { bountyApi } from '../services/api';
import { Bounty } from '../types/api';
import { 
  MagnifyingGlassIcon, 
  FunnelIcon,
  CurrencyDollarIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon 
} from '@heroicons/react/24/outline';
import { CodeBracketIcon } from '@heroicons/react/24/outline';
import { useToast } from '../components/ui/Toast';
import { SkeletonText } from '../components/ui/Skeleton';

const Bounties: React.FC = () => {
  const [bounties, setBounties] = useState<Bounty[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const location = useLocation();
  const navigate = useNavigate();
  const params = useMemo(() => new URLSearchParams(location.search), [location.search]);
  const [searchTerm, setSearchTerm] = useState(params.get('q') ?? '');
  const [statusFilter, setStatusFilter] = useState(params.get('status') ?? 'all');
  const [sortBy, setSortBy] = useState(params.get('sort') ?? 'amount');
  const { showToast } = useToast();

  useEffect(() => {
    fetchBounties();
  }, []);

  const fetchBounties = async () => {
    try {
      setLoading(true);
      const data = await bountyApi.listBounties();
      setBounties(data);
    } catch (error) {
      setError('Failed to load bounties');
      console.error('Error fetching bounties:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      fetchBounties();
      return;
    }

    try {
      setLoading(true);
      const next = new URLSearchParams(location.search);
      next.set('q', searchTerm);
      navigate({ pathname: '/bounties', search: next.toString() }, { replace: true });
      const data = await bountyApi.searchBounties(searchTerm);
      setBounties(data);
    } catch (error) {
      setError('Search failed');
      showToast('Search failed', 'error');
      console.error('Error searching bounties:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusFilter = async (status: string) => {
    setStatusFilter(status);
    const next = new URLSearchParams(location.search);
    next.set('status', status);
    navigate({ pathname: '/bounties', search: next.toString() }, { replace: true });
    
    if (status === 'all') {
      fetchBounties();
      return;
    }

    try {
      setLoading(true);
      const data = await bountyApi.getBountiesByStatus(status);
      setBounties(data);
    } catch (error) {
      setError('Failed to filter bounties');
      console.error('Error filtering bounties:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'open':
        return (
          <span className="badge-success">
            <CheckCircleIcon className="h-3 w-3 mr-1" />
            Open
          </span>
        );
      case 'accepted':
        return (
          <span className="badge-warning">
            <ClockIcon className="h-3 w-3 mr-1" />
            In Progress
          </span>
        );
      case 'claimed':
        return (
          <span className="badge-info">
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

  const extractRepoName = (githubUrl: string) => {
    const match = githubUrl.match(/github\.com\/([^/]+\/[^/]+)/);
    if (match) {
      return match[1];
    }
    return 'Unknown Repository';
  };

  const filteredAndSortedBounties = bounties
    .filter(bounty => 
      bounty.bounty_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      bounty.github_issue_url.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => {
      switch (sortBy) {
        case 'amount':
          return b.amount - a.amount;
        case 'created_at':
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        default:
          return 0;
      }
    });

  const Segmented = (
    <div className="inline-flex rounded-xl border border-neutral-700 overflow-hidden h-12">
      {[
        { key: 'all', label: 'All' },
        { key: 'open', label: 'Open' },
        { key: 'accepted', label: 'In Progress' },
        { key: 'claimed', label: 'Completed' },
      ].map(item => (
        <button
          key={item.key}
          onClick={() => handleStatusFilter(item.key)}
          className={`px-4 text-sm transition-colors h-full ${
            statusFilter === item.key
              ? 'bg-blue-500/20 text-white border-r border-neutral-700'
              : 'text-neutral-300 hover:bg-neutral-800/50 border-r border-neutral-700'
          }`}
        >
          {item.label}
        </button>
      ))}
    </div>
  );

  const handleSort = (value: string) => {
    setSortBy(value);
    const next = new URLSearchParams(location.search);
    next.set('sort', value);
    navigate({ pathname: '/bounties', search: next.toString() }, { replace: true });
  };

  const SortSegmented = (
    <div className="inline-flex rounded-xl border border-neutral-700 overflow-hidden h-12">
      {[
        { key: 'amount', label: 'Highest Amount' },
        { key: 'created_at', label: 'Newest' },
      ].map(item => (
        <button
          key={item.key}
          onClick={() => handleSort(item.key)}
          className={`px-4 text-sm transition-colors h-full ${
            sortBy === item.key
              ? 'bg-blue-500/20 text-white border-r border-neutral-700'
              : 'text-neutral-300 hover:bg-neutral-800/50 border-r border-neutral-700'
          }`}
        >
          {item.label}
        </button>
      ))}
    </div>
  );

  return (
    <div className="space-y-6 fade-in">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white">Bounties</h1>
          <p className="text-gray-300 mt-1">
            Find and work on exciting projects
          </p>
        </div>
        <Link to="/bounties/create" className="btn-primary">
          Create Bounty
        </Link>
      </div>

      <div className="card">
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <input
                type="text"
                placeholder="Search bounties by name or GitHub URL..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                className="input-field pr-10"
              />
              <button
                onClick={handleSearch}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-300"
              >
                <MagnifyingGlassIcon className="h-5 w-5" />
              </button>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <FunnelIcon className="h-5 w-5 text-gray-400" />
            {Segmented}
          </div>

          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-300">Sort:</span>
            {SortSegmented}
          </div>
        </div>
      </div>

      {error && (
        <div className="error-message">
          <ExclamationTriangleIcon className="h-5 w-5 mr-2" />
          {error}
        </div>
      )}

      {loading ? (
        <div className="grid gap-6 md:grid-cols-2">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="card-compact">
              <SkeletonText className="h-5 w-3/4 mb-4" />
              <SkeletonText className="h-4 w-1/2 mb-3" />
              <SkeletonText className="h-4 w-full mb-3" />
              <SkeletonText className="h-4 w-2/3" />
            </div>
          ))}
        </div>
      ) : filteredAndSortedBounties.length === 0 ? (
        <div className="text-center py-12">
          <CurrencyDollarIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-white mb-2">No bounties found</h3>
          <p className="text-gray-400">
            {searchTerm ? 'Try adjusting your search terms.' : 'Be the first to create a bounty!'}
          </p>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2">
          {filteredAndSortedBounties.map((bounty) => (
            <Link
              key={bounty.id}
              to={`/bounties/${bounty.id}`}
              className="card-hover"
            >
              <div className="space-y-4">
                <div className="flex justify-between items-start">
                  <h3 className="text-lg font-semibold text-white line-clamp-2">
                    {formatBountyName(bounty.bounty_name)}
                  </h3>
                  {getStatusBadge(bounty.status)}
                </div>
                
                <div className="text-sm text-blue-400 font-medium inline-flex items-center gap-2">
                  <span className="inline-flex items-center px-2 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-300">
                    <CodeBracketIcon className="h-4 w-4 mr-1" />
                    {extractRepoName(bounty.github_issue_url)}
                  </span>
                  {bounty.escrow_id && (
                    <span className="inline-flex items-center px-2 py-1 rounded-full bg-success-500/10 border border-success-500/20 text-success-400">
                      <CheckCircleIcon className="h-4 w-4 mr-1" />
                      Escrowed
                    </span>
                  )}
                </div>
                
                {bounty.description && (
                  <div className="text-sm text-gray-300 line-clamp-3">
                    {bounty.description}
                  </div>
                )}
                
                <div className="flex items-center justify-between text-sm text-gray-300">
                  <span className="flex items-center">
                    <CurrencyDollarIcon className="h-4 w-4 mr-1" />
                    {bounty.amount} XRP
                  </span>
                  <span>{formatDate(bounty.created_at)}</span>
                </div>
                
                <div className="text-sm text-gray-400 truncate">
                  {bounty.github_issue_url}
                </div>
                
                {bounty.developer_address && (
                  <div className="text-xs text-gray-500">
                    Developer: {bounty.developer_address.slice(0, 8)}...{bounty.developer_address.slice(-8)}
                  </div>
                )}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

export default Bounties; 