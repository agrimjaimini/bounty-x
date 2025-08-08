import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';

// Simple top progress bar that animates on route change
const ProgressBar: React.FC = () => {
  const location = useLocation();
  const [active, setActive] = useState(false);

  useEffect(() => {
    setActive(true);
    const t = setTimeout(() => setActive(false), 400);
    return () => clearTimeout(t);
  }, [location.pathname]);

  return (
    <div className="pointer-events-none fixed top-0 left-0 right-0 z-50">
      <div
        className={`h-0.5 bg-gradient-to-r from-blue-500 via-accent-500 to-success-500 transition-all duration-300 ${
          active ? 'w-full opacity-100' : 'w-0 opacity-0'
        }`}
      />
    </div>
  );
};

export default ProgressBar;

