import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
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

const Bounties: React.FC = () => {
  const [bounties, setBounties] = useState<Bounty[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortBy, setSortBy] = useState('created_at');

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
      const data = await bountyApi.searchBounties(searchTerm);
      setBounties(data);
    } catch (error) {
      setError('Search failed');
      console.error('Error searching bounties:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusFilter = async (status: string) => {
    setStatusFilter(status);
    
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
    // Clean up the bounty name for better readability
    return name
      .replace(/_/g, ' ')  // Replace underscores with spaces
      .replace(/-/g, ' ')  // Replace hyphens with spaces
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="spinner h-12 w-12"></div>
      </div>
    );
  }

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

      {/* Search and Filters */}
      <div className="card">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Search */}
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

          {/* Status Filter */}
          <div className="flex items-center space-x-2">
            <FunnelIcon className="h-5 w-5 text-gray-400" />
            <select
              value={statusFilter}
              onChange={(e) => handleStatusFilter(e.target.value)}
              className="input-field w-auto"
            >
              <option value="all">All Status</option>
              <option value="open">Open</option>
              <option value="accepted">In Progress</option>
              <option value="claimed">Completed</option>
            </select>
          </div>

          {/* Sort */}
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-300">Sort by:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="input-field w-auto"
            >
              <option value="created_at">Newest</option>
              <option value="amount">Highest Amount</option>
            </select>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="error-message">
          <ExclamationTriangleIcon className="h-5 w-5 mr-2" />
          {error}
        </div>
      )}

      {/* Bounties Grid */}
      {filteredAndSortedBounties.length === 0 ? (
        <div className="text-center py-12">
          <CurrencyDollarIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-white mb-2">No bounties found</h3>
          <p className="text-gray-400">
            {searchTerm ? 'Try adjusting your search terms.' : 'Be the first to create a bounty!'}
          </p>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
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