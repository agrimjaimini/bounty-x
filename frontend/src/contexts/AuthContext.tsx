import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User } from '../types/api';
import { userApi } from '../services/api';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in on app start
    const userId = localStorage.getItem('userId');
    if (userId) {
      userApi.getUser(parseInt(userId))
        .then((userData) => {
          setUser(userData);
        })
        .catch(() => {
          localStorage.removeItem('userId');
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (username: string, password: string) => {
    try {
      const response = await userApi.login({ username, password });
      // The login response now includes all user data
      const userData: User = {
        id: response.user_id,
        username: response.username,
        xrp_address: response.xrp_address,
        bounties_created: response.bounties_created,
        bounties_accepted: response.bounties_accepted,
        total_xrp_funded: response.total_xrp_funded,
        total_xrp_earned: response.total_xrp_earned,
        current_xrp_balance: response.current_xrp_balance,
        last_updated: response.last_updated,
      };
      setUser(userData);
      localStorage.setItem('userId', response.user_id.toString());
    } catch (error) {
      throw error;
    }
  };

  const register = async (username: string, password: string) => {
    try {
      const response = await userApi.register({ username, password });
      const userData = await userApi.getUser(response.user_id);
      setUser(userData);
      localStorage.setItem('userId', response.user_id.toString());
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('userId');
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 