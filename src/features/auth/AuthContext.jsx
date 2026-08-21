import React, { createContext, useContext, useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://your-project.supabase.co';
const supabaseKey = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY || 'replace_with_publishable_key';

const isSupabaseConfigured = supabaseUrl && !supabaseUrl.includes('your-project') && supabaseKey && !supabaseKey.includes('replace_with');

export const supabase = isSupabaseConfigured
  ? createClient(supabaseUrl, supabaseKey)
  : createClient('https://mock.supabase.co', 'mock-key');

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);

  // Helper to determine if user has admin role
  const checkIsAdmin = (userData) => {
    if (!userData) return false;
    const email = (userData.email || '').toLowerCase();
    const role = (userData.role || userData.user_metadata?.role || '').toLowerCase();
    
    // Check configured admin emails list
    const adminEmailsConfig = (import.meta.env.VITE_ADMIN_EMAILS || '').toLowerCase().split(',').map(e => e.trim());
    if (adminEmailsConfig.includes(email)) return true;
    
    return role === 'admin' || email.startsWith('admin@') || email.includes('admin');
  };

  useEffect(() => {
    const checkSession = async () => {
      try {
        if (isSupabaseConfigured) {
          const { data } = await supabase.auth.getSession();
          if (data?.session) {
            setSession(data.session);
            const isAdmin = checkIsAdmin(data.session.user);
            setUser({
              id: data.session.user.id,
              email: data.session.user.email,
              role: isAdmin ? 'admin' : (data.session.user.role || 'researcher'),
              isAdmin: isAdmin,
              fullName: data.session.user.user_metadata?.full_name || data.session.user.email?.split('@')[0],
            });
            localStorage.setItem('lawverse_auth_token', data.session.access_token);
          } else {
            setUser(null);
            localStorage.removeItem('lawverse_auth_token');
          }
        } else {
          // Check local storage for offline session if any
          const savedUser = localStorage.getItem('lawverse_user_profile');
          if (savedUser) {
            try {
              const parsed = JSON.parse(savedUser);
              setUser(parsed);
            } catch (e) {
              setUser(null);
            }
          } else {
            setUser(null);
          }
        }
      } catch (err) {
        console.warn('Session check warning:', err);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    checkSession();

    if (isSupabaseConfigured) {
      const { data: authListener } = supabase.auth.onAuthStateChange((event, newSession) => {
        if (newSession) {
          setSession(newSession);
          const isAdmin = checkIsAdmin(newSession.user);
          const userObj = {
            id: newSession.user.id,
            email: newSession.user.email,
            role: isAdmin ? 'admin' : (newSession.user.role || 'researcher'),
            isAdmin: isAdmin,
            fullName: newSession.user.user_metadata?.full_name || newSession.user.email?.split('@')[0],
          };
          setUser(userObj);
          localStorage.setItem('lawverse_auth_token', newSession.access_token);
        } else {
          setSession(null);
          setUser(null);
          localStorage.removeItem('lawverse_auth_token');
        }
      });

      return () => {
        authListener?.subscription?.unsubscribe();
      };
    }
  }, []);

  const login = async (email, password) => {
    setLoading(true);
    try {
      if (isSupabaseConfigured) {
        const { data, error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
        const isAdmin = checkIsAdmin(data.user);
        const userObj = {
          id: data.user.id,
          email: data.user.email,
          role: isAdmin ? 'admin' : (data.user.role || 'researcher'),
          isAdmin: isAdmin,
          fullName: data.user.user_metadata?.full_name || data.user.email?.split('@')[0],
        };
        setUser(userObj);
        localStorage.setItem('lawverse_auth_token', data.session.access_token);
        return userObj;
      } else {
        // Fallback local auth when Supabase credentials are being configured
        const isAdmin = email.toLowerCase().includes('admin');
        const simulatedUser = {
          id: 'user_' + Date.now(),
          email,
          role: isAdmin ? 'admin' : 'researcher',
          isAdmin: isAdmin,
          fullName: email.split('@')[0]
        };
        setUser(simulatedUser);
        localStorage.setItem('lawverse_user_profile', JSON.stringify(simulatedUser));
        localStorage.setItem('lawverse_auth_token', 'dev_token');
        return simulatedUser;
      }
    } finally {
      setLoading(false);
    }
  };

  const signup = async (email, password, fullName) => {
    setLoading(true);
    try {
      if (isSupabaseConfigured) {
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
          options: {
            data: {
              full_name: fullName,
              role: email.toLowerCase().includes('admin') ? 'admin' : 'researcher'
            }
          }
        });
        if (error) throw error;
        if (data.user && data.session) {
          const isAdmin = checkIsAdmin(data.user);
          const userObj = {
            id: data.user.id,
            email: data.user.email,
            role: isAdmin ? 'admin' : 'researcher',
            isAdmin: isAdmin,
            fullName: fullName || email.split('@')[0],
          };
          setUser(userObj);
          localStorage.setItem('lawverse_auth_token', data.session.access_token);
          return userObj;
        }
        return data;
      } else {
        const isAdmin = email.toLowerCase().includes('admin');
        const simulatedUser = {
          id: 'user_' + Date.now(),
          email,
          role: isAdmin ? 'admin' : 'researcher',
          isAdmin: isAdmin,
          fullName: fullName || email.split('@')[0]
        };
        setUser(simulatedUser);
        localStorage.setItem('lawverse_user_profile', JSON.stringify(simulatedUser));
        localStorage.setItem('lawverse_auth_token', 'dev_token');
        return simulatedUser;
      }
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      if (isSupabaseConfigured) {
        await supabase.auth.signOut();
      }
    } catch (e) {
      console.warn('Logout warning:', e);
    } finally {
      setUser(null);
      setSession(null);
      localStorage.removeItem('lawverse_auth_token');
      localStorage.removeItem('lawverse_user_profile');
    }
  };

  return (
    <AuthContext.Provider value={{ user, session, loading, login, signup, logout, isSupabaseConfigured }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
