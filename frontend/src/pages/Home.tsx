import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { bountyApi } from '../services/api';
import { BountyStatistics } from '../types/api';
import { 
  CurrencyDollarIcon, 
  CodeBracketIcon, 
  ShieldCheckIcon,
  RocketLaunchIcon,
  ArrowRightIcon 
} from '@heroicons/react/24/outline';

const Home: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<BountyStatistics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await bountyApi.getBountyStatistics();
        setStats(data);
      } catch (error) {
        console.error('Failed to fetch statistics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const features = [
    {
      icon: CurrencyDollarIcon,
      title: 'Decentralized Bounties',
      description: 'Create and fund bounties using XRP cryptocurrency with secure escrow services.',
      gradient: 'from-primary-500 to-primary-600',
    },
    {
      icon: CodeBracketIcon,
      title: 'GitHub Integration',
      description: 'Seamlessly link bounties to GitHub issues and verify merge requests.',
      gradient: 'from-accent-500 to-accent-600',
    },
    {
      icon: ShieldCheckIcon,
      title: 'Secure Escrow',
      description: 'Conditional escrow ensures funds are only released when work is completed.',
      gradient: 'from-success-500 to-success-600',
    },
    {
      icon: RocketLaunchIcon,
      title: 'Fast Payments',
      description: 'Instant XRP payments once bounty conditions are met.',
      gradient: 'from-warning-500 to-warning-600',
    },
  ];

  return (
    <div className="space-y-16 fade-in">
      {/* Hero Section */}
      <section className="text-center py-20">
        <div className="max-w-4xl mx-auto">
          <div className="relative mb-8">
            <h1 className="text-6xl font-bold gradient-text mb-6">
              Decentralized Bounty Platform
            </h1>
            <div className="absolute inset-0 bg-gradient-to-r from-primary-500/20 to-accent-500/20 blur-3xl -z-10"></div>
          </div>
          <p className="text-xl text-gray-300 mb-12 max-w-2xl mx-auto leading-relaxed">
            Connect developers with projects through secure, blockchain-powered bounties. 
            Fund issues, verify work, and get paid instantly with XRP.
          </p>
          <div className="flex flex-col sm:flex-row gap-6 justify-center">
            {user ? (
              <>
                <Link to="/bounties" className="btn-primary text-lg px-8 py-4">
                  Browse Bounties
                </Link>
                <Link to="/bounties/create" className="btn-accent text-lg px-8 py-4">
                  Create Bounty
                </Link>
              </>
            ) : (
              <>
                <Link to="/register" className="btn-primary text-lg px-8 py-4">
                  Get Started
                </Link>
                <Link to="/bounties" className="btn-secondary text-lg px-8 py-4">
                  Browse Bounties
                </Link>
              </>
            )}
          </div>
        </div>
      </section>

      {/* Statistics Section */}
      {!loading && stats && (
        <section className="card slide-up">
          <h2 className="text-3xl font-bold text-center mb-8 gradient-text">
            Platform Statistics
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="text-center group">
              <div className="relative">
                <div className="text-4xl font-bold text-primary-400 mb-2 group-hover:scale-110 transition-transform duration-200">
                  {stats.total_bounties}
                </div>
                <div className="absolute inset-0 bg-primary-500/10 rounded-full blur-sm group-hover:bg-primary-500/20 transition-all duration-200"></div>
              </div>
              <div className="text-gray-400">Total Bounties</div>
            </div>
            <div className="text-center group">
              <div className="relative">
                <div className="text-4xl font-bold text-success-400 mb-2 group-hover:scale-110 transition-transform duration-200">
                  {stats.open_bounties}
                </div>
                <div className="absolute inset-0 bg-success-500/10 rounded-full blur-sm group-hover:bg-success-500/20 transition-all duration-200"></div>
              </div>
              <div className="text-gray-400">Open Bounties</div>
            </div>
            <div className="text-center group">
              <div className="relative">
                <div className="text-4xl font-bold text-warning-400 mb-2 group-hover:scale-110 transition-transform duration-200">
                  {stats.accepted_bounties}
                </div>
                <div className="absolute inset-0 bg-warning-500/10 rounded-full blur-sm group-hover:bg-warning-500/20 transition-all duration-200"></div>
              </div>
              <div className="text-gray-400">In Progress</div>
            </div>
            <div className="text-center group">
              <div className="relative">
                <div className="text-4xl font-bold text-accent-400 mb-2 group-hover:scale-110 transition-transform duration-200">
                  {stats.total_amount} XRP
                </div>
                <div className="absolute inset-0 bg-accent-500/10 rounded-full blur-sm group-hover:bg-accent-500/20 transition-all duration-200"></div>
              </div>
              <div className="text-gray-400">Total Value</div>
            </div>
          </div>
        </section>
      )}

      {/* Features Section */}
      <section className="slide-up">
        <h2 className="text-4xl font-bold text-center mb-16 gradient-text">
          Why Choose Bounty-X?
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="card-hover group">
              <div className="text-center">
                <div className={`inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-r ${feature.gradient} mb-6 group-hover:scale-110 transition-transform duration-200`}>
                  <feature.icon className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-white mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-400 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative overflow-hidden rounded-3xl">
        <div className="absolute inset-0 bg-gradient-to-r from-primary-600/20 to-accent-600/20 backdrop-blur-sm"></div>
        <div className="relative p-12 text-center">
          <h2 className="text-4xl font-bold mb-6 text-white">
            Ready to Get Started?
          </h2>
          <p className="text-xl mb-8 text-gray-200">
            Join the decentralized bounty economy today.
          </p>
          <div className="flex flex-col sm:flex-row gap-6 justify-center">
            {user ? (
              <Link to="/bounties/create" className="btn-accent text-lg px-8 py-4 flex items-center justify-center space-x-2">
                <span>Create Your First Bounty</span>
                <ArrowRightIcon className="h-5 w-5" />
              </Link>
            ) : (
              <Link to="/register" className="btn-accent text-lg px-8 py-4 flex items-center justify-center space-x-2">
                <span>Sign Up Now</span>
                <ArrowRightIcon className="h-5 w-5" />
              </Link>
            )}
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home; 