import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { bountyApi } from '../services/api';
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline';

const CreateBounty: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    bounty_name: '',
    description: '',
    github_issue_url: '',
    amount: '',
    finish_after: '86400', // Default 24 hours
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError('');
  };

  const validateForm = () => {
    if (!formData.bounty_name.trim()) {
      setError('Bounty name is required');
      return false;
    }
    if (!formData.description.trim()) {
      setError('Description is required');
      return false;
    }
    if (!formData.github_issue_url.trim()) {
      setError('GitHub issue URL is required');
      return false;
    }
    if (!formData.github_issue_url.includes('github.com')) {
      setError('Please enter a valid GitHub issue URL');
      return false;
    }
    if (!formData.amount || parseFloat(formData.amount) <= 0) {
      setError('Please enter a valid amount greater than 0');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError('');

    try {
      await bountyApi.createBounty({
        funder_id: user!.id,
        bounty_name: formData.bounty_name.trim(),
        description: formData.description.trim(),
        github_issue_url: formData.github_issue_url.trim(),
        amount: parseFloat(formData.amount),
        finish_after: parseInt(formData.finish_after),
      });
      navigate('/bounties');
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail;
      setError(typeof errorMessage === 'string' ? errorMessage : 'Failed to create bounty. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto fade-in">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Create New Bounty</h1>
        <p className="text-gray-300 mt-2">
          Fund a GitHub issue and let developers work on it
        </p>
      </div>

      <form onSubmit={handleSubmit} className="card space-y-6">
        <div>
          <label htmlFor="bounty_name" className="form-label">
            Bounty Name *
          </label>
          <input
            id="bounty_name"
            name="bounty_name"
            type="text"
            required
            value={formData.bounty_name}
            onChange={handleChange}
            className="input-field"
            placeholder="e.g., Fix login authentication bug"
          />
          <p className="mt-2 text-sm text-gray-400">
            Choose a clear, descriptive name for your bounty
          </p>
        </div>

        <div>
          <label htmlFor="description" className="form-label">
            Description *
          </label>
          <textarea
            id="description"
            name="description"
            required
            rows={4}
            value={formData.description}
            onChange={handleChange}
            className="input-field"
            placeholder="Provide a detailed description of what needs to be done, requirements, and any specific instructions for developers..."
          />
          <p className="mt-2 text-sm text-gray-400">
            Detailed description of the work to be completed
          </p>
        </div>

        <div>
          <label htmlFor="github_issue_url" className="form-label">
            GitHub Issue URL *
          </label>
          <input
            id="github_issue_url"
            name="github_issue_url"
            type="url"
            required
            value={formData.github_issue_url}
            onChange={handleChange}
            className="input-field"
            placeholder="https://github.com/username/repo/issues/123"
          />
          <p className="mt-2 text-sm text-gray-400">
            Link to the GitHub issue that needs to be resolved
          </p>
        </div>

        <div>
          <label htmlFor="amount" className="form-label">
            Bounty Amount (XRP) *
          </label>
          <div className="relative">
            <input
              id="amount"
              name="amount"
              type="number"
              step="0.1"
              min="0.1"
              required
              value={formData.amount}
              onChange={handleChange}
              className="input-field pr-12"
              placeholder="10.0"
            />
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
              <span className="text-gray-400 sm:text-sm">XRP</span>
            </div>
          </div>
          <p className="mt-2 text-sm text-gray-400">
            Amount will be held in escrow until the bounty is completed
          </p>
        </div>

        <div>
          <label htmlFor="finish_after" className="form-label">
            Time Limit
          </label>
          <select
            id="finish_after"
            name="finish_after"
            value={formData.finish_after}
            onChange={handleChange}
            className="input-field"
          >
            <option value="3600">1 hour</option>
            <option value="86400">24 hours</option>
            <option value="604800">1 week</option>
            <option value="2592000">1 month</option>
          </select>
          <p className="mt-2 text-sm text-gray-400">
            Time limit for completing the bounty after acceptance
          </p>
        </div>

        {error && (
          <div className="error-message">
            <ExclamationTriangleIcon className="h-5 w-5 mr-2" />
            {error}
          </div>
        )}

        <div className="bg-primary-500/10 border border-primary-500/30 rounded-xl p-4">
          <h3 className="text-sm font-medium text-primary-400 mb-2">Important Information</h3>
          <ul className="text-sm text-gray-300 space-y-1">
            <li>• Your XRP will be held in a conditional escrow</li>
            <li>• Funds are only released when the bounty is completed and verified</li>
            <li>• You can cancel the escrow if no one accepts within the time limit</li>
            <li>• Make sure the GitHub issue URL is accessible and well-described</li>
          </ul>
        </div>

        <div className="flex gap-4">
          <button
            type="button"
            onClick={() => navigate('/bounties')}
            className="btn-secondary flex-1"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="btn-primary flex-1 relative overflow-hidden"
          >
            {loading ? (
              <>
                <div className="flex items-center justify-center">
                  <div className="spinner h-5 w-5 mr-2"></div>
                  <span>Funding...</span>
                </div>
                <div className="absolute bottom-0 left-0 h-1 bg-white/20 animate-pulse" style={{ width: '100%' }}></div>
              </>
            ) : (
              'Create Bounty'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default CreateBounty; 