import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
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

  const steps = [
    {
      icon: CurrencyDollarIcon,
      title: 'Create a bounty',
      description: 'Post a GitHub issue and fund it with testnet XRP held in escrow.',
      ring: 'bg-primary-500/20 ring-primary-500/30',
      iconColor: 'text-primary-300',
    },
    {
      icon: CodeBracketIcon,
      title: 'Accept and build',
      description: 'A developer accepts the bounty and starts working on the task.',
      ring: 'bg-accent-500/20 ring-accent-500/30',
      iconColor: 'text-accent-300',
    },
    {
      icon: ShieldCheckIcon,
      title: 'Submit your PR',
      description: 'Open a pull request that references the issue for verification.',
      ring: 'bg-success-500/20 ring-success-500/30',
      iconColor: 'text-success-300',
    },
    {
      icon: RocketLaunchIcon,
      title: 'Claim your reward',
      description: 'Once merged and verified, escrow releases XRP instantly.',
      ring: 'bg-warning-500/20 ring-warning-500/30',
      iconColor: 'text-warning-300',
    },
  ];

  const [activeStep, setActiveStep] = useState(0);
  const [direction, setDirection] = useState(1);
  const ActiveIcon = steps[activeStep].icon;

  const goToStep = (nextIndex: number) => {
    const clamped = Math.max(0, Math.min(steps.length - 1, nextIndex));
    setDirection(clamped > activeStep ? 1 : clamped < activeStep ? -1 : direction);
    setActiveStep(clamped);
  };

  return (
    <div className="space-y-16 fade-in">
      <section className="relative overflow-hidden rounded-3xl border border-neutral-800/50 bg-neutral-950/50 backdrop-blur-sm">
        <div className="pointer-events-none absolute -top-24 -left-24 h-96 w-96 rounded-full bg-blue-500/10 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-24 -right-24 h-96 w-96 rounded-full bg-blue-600/10 blur-3xl" />
        <div className="relative grid items-center gap-10 px-8 py-16 md:px-12 lg:grid-cols-2 lg:py-20">
          <div className="relative z-10">
            <div className="inline-flex items-center gap-2 rounded-full border border-blue-500/20 bg-blue-500/10 px-3 py-1 text-sm text-blue-300 mb-6">
              Powered by the XRP Ledger
            </div>
            <h1 className="mb-6 text-5xl font-bold gradient-text sm:text-6xl">
              Decentralized Bounties, Supercharged by the XRP Ledger
            </h1>
            <p className="text-xl leading-relaxed text-gray-300 max-w-prose">
              Create, fund, and complete bounties with secure escrow and lightning-fast payments. Connect open-source work to real incentives.
            </p>
            <div className="mt-10 flex flex-col gap-4 sm:flex-row">
              {user ? (
                <>
                  <Link to="/bounties" className="btn-primary btn-lg">
                    Browse Bounties
                  </Link>
                  <Link to="/bounties/create" className="btn-accent btn-lg">
                    Create Bounty
                  </Link>
                </>
              ) : (
                <>
                  <Link to="/register" className="btn-primary btn-lg">
                    Get Started
                  </Link>
                  <Link to="/bounties" className="btn-secondary btn-lg">
                    Explore Marketplace
                  </Link>
                </>
              )}
            </div>
          </div>
          <InteractiveXrpLogo />
        </div>
      </section>

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

      <section className="slide-up">
        <h2 className="text-4xl font-bold text-center mb-16 gradient-text">How it works</h2>
        <div className="max-w-5xl mx-auto">
            <div 
            className="relative px-2 md:px-6"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'ArrowRight') goToStep(activeStep + 1);
              if (e.key === 'ArrowLeft') goToStep(activeStep - 1);
            }}
          >
            <div className="hidden md:block absolute left-6 right-6 top-6 h-0.5 bg-neutral-800" />
            <motion.div
              className="hidden md:block absolute left-6 top-6 h-0.5 bg-blue-500/60"
              animate={{ width: `${(activeStep / (steps.length - 1)) * 100}%` }}
              transition={{ type: 'spring', stiffness: 200, damping: 24 }}
            />
            <div className="relative z-10 grid grid-cols-4 gap-4 md:gap-8">
              {steps.map((step, idx) => (
                <button
                  key={step.title}
                  onClick={() => goToStep(idx)}
                  className={`group flex flex-col items-center text-center focus:outline-none ${idx < steps.length - 1 ? '' : ''}`}
                  aria-current={activeStep === idx}
                >
                  <motion.div
                    className={`h-12 w-12 rounded-full ring-2 flex items-center justify-center ${
                      activeStep >= idx ? step.ring : 'bg-neutral-800/80 ring-neutral-700'
                    }`}
                    animate={{ scale: activeStep === idx ? 1.08 : 1 }}
                    whileHover={{ scale: 1.06 }}
                    whileTap={{ scale: 0.96 }}
                    transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                  >
                    <step.icon className={`h-6 w-6 ${activeStep >= idx ? step.iconColor : 'text-neutral-400'}`} />
                  </motion.div>
                  <span className={`mt-3 text-sm font-medium ${activeStep >= idx ? 'text-white' : 'text-neutral-400 group-hover:text-neutral-300'}`}>
                    {step.title}
                  </span>
                </button>
              ))}
            </div>
          </div>

          <AnimatePresence mode="wait" custom={direction}>
            <motion.div
              key={activeStep}
              custom={direction}
              initial="enter"
              animate="center"
              exit="exit"
              variants={{
                enter: (dir: number) => ({ opacity: 0, x: dir * 24, scale: 0.98 }),
                center: { opacity: 1, x: 0, scale: 1, transition: { type: 'spring', stiffness: 320, damping: 28 } },
                exit: (dir: number) => ({ opacity: 0, x: -dir * 24, scale: 0.98, transition: { duration: 0.18 } })
              }}
              className="mt-6 md:mt-8"
            >
              <div className="card card-compact max-w-xl mx-auto">
              <div className="flex items-start gap-3">
                  <div className="h-9 w-9 rounded-full bg-neutral-800/80 flex items-center justify-center ring-1 ring-neutral-700">
                    <motion.div
                      key={`icon-${activeStep}`}
                      initial={{ scale: 0.9, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      transition={{ type: 'spring', stiffness: 320, damping: 22 }}
                    >
                      <ActiveIcon className={`h-5 w-5 ${steps[activeStep].iconColor}`} />
                    </motion.div>
                  </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">{steps[activeStep].title}</h3>
                  <p className="text-gray-400 mt-1">{steps[activeStep].description}</p>
                </div>
              </div>
              </div>
            </motion.div>
          </AnimatePresence>
        </div>
      </section>

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

const InteractiveXrpLogo: React.FC = () => {
  return (
    <div className="relative z-10 mx-auto w-full max-w-lg">
      <div className="relative aspect-square w-full">
        <div
          className="absolute inset-6 z-0 rounded-full animate-[spin_60s_linear_infinite]"
          style={{
            background:
              'repeating-conic-gradient(from 0deg, rgba(59,130,246,0.25) 0deg 10deg, transparent 10deg 22deg)',
            WebkitMask:
              'radial-gradient(farthest-side, transparent calc(100% - 3px), #000 calc(100% - 3px))',
            mask:
              'radial-gradient(farthest-side, transparent calc(100% - 3px), #000 calc(100% - 3px))',
            filter: 'drop-shadow(0 0 6px rgba(59,130,246,0.18))',
          } as React.CSSProperties}
        />
        <div
          className="absolute inset-16 z-0 rounded-full animate-[spin_30s_linear_infinite]"
          style={{
            background: 'rgba(125,211,252,0.22)',
            WebkitMask:
              'radial-gradient(farthest-side, transparent calc(100% - 2px), #000 calc(100% - 2px))',
            mask:
              'radial-gradient(farthest-side, transparent calc(100% - 2px), #000 calc(100% - 2px))',
            filter: 'drop-shadow(0 0 4px rgba(56,189,248,0.18))',
            animationDirection: 'reverse',
          } as React.CSSProperties}
        />
        <div className="absolute inset-0 z-0 rounded-3xl bg-gradient-to-br from-blue-500/10 via-transparent to-blue-500/5" />
        <div className="absolute inset-0 z-10 flex items-center justify-center">
          <img
            src="/xrp-logo.svg"
            alt="XRP Logo"
            className="h-40 w-40 filter invert drop-shadow-[0_0_30px_rgba(255,255,255,0.25)]"
          />
        </div>
      </div>
    </div>
  );
};