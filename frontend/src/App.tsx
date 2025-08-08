import React from 'react';
import { HashRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { AuthProvider } from './contexts/AuthContext';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Bounties from './pages/Bounties';
import CreateBounty from './pages/CreateBounty';
import BountyDetail from './pages/BountyDetail';
import Profile from './pages/Profile';
import ProtectedRoute from './components/ProtectedRoute';
import ProgressBar from './components/ui/ProgressBar';
import ScrollToTop from './components/util/ScrollToTop';

const Page: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <motion.div
    initial={{ opacity: 0, y: 8 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -8 }}
    transition={{ duration: 0.18, ease: 'easeOut' }}
    layout
  >
    {children}
  </motion.div>
);

const AnimatedRoutes: React.FC = () => {
  const location = useLocation();
  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<Page><Home /></Page>} />
        <Route path="/login" element={<Page><Login /></Page>} />
        <Route path="/register" element={<Page><Register /></Page>} />
        <Route path="/bounties" element={<Page><Bounties /></Page>} />
        <Route 
          path="/bounties/create" 
          element={
            <ProtectedRoute>
              <Page><CreateBounty /></Page>
            </ProtectedRoute>
          } 
        />
        <Route path="/bounties/:id" element={<Page><BountyDetail /></Page>} />
        <Route 
          path="/profile" 
          element={
            <ProtectedRoute>
              <Page><Profile /></Page>
            </ProtectedRoute>
          } 
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AnimatePresence>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen animated-bg flex flex-col">
          <ProgressBar />
          <ScrollToTop />
          <Navbar />
          <main className="max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-10 flex-grow">
            <AnimatedRoutes />
          </main>
          <Footer />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
