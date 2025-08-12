import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="relative bg-neutral-950/60 backdrop-blur-sm border-t border-neutral-800/50 mt-auto">
      <div className="pointer-events-none absolute inset-x-0 -top-px h-px bg-gradient-to-r from-transparent via-blue-500/30 to-transparent" />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <span className="text-neutral-400 text-sm">
              © 2025 Agrim Jaimini. 
            </span>
          </div>
          
          <div className="flex items-center space-x-6 text-sm">
            <a 
              href="https://xrpl.org" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-neutral-400 hover:text-blue-400 transition-colors duration-200"
            >
              XRPL Foundation
            </a>
            <a 
              href="https://github.com" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-neutral-400 hover:text-blue-400 transition-colors duration-200"
            >
              GitHub
            </a>
          </div>
        </div>
        
        <div className="mt-4 pt-4 border-t border-neutral-800/30">
          <div className="text-center text-xs text-neutral-500">
            <p>
              Bounty-X is a decentralized bounty platform built on the XRP Ledger. 
              Connect, collaborate, and earn rewards for your contributions to the ecosystem.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer; 