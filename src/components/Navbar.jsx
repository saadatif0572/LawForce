import React, { useState } from 'react';
import { Scale, BookOpen, MessageSquare, ShieldCheck, UserCheck, LogOut, Lock, Database, ShieldAlert } from 'lucide-react';
import { useAuth } from '../features/auth/AuthContext';
import AuthModal from './AuthModal';

export default function Navbar({ activeTab, setActiveTab }) {
  const { user, logout } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);

  // Base navigation items visible to all
  const navItems = [
    { id: 'landing', label: 'Home', icon: Scale },
    { id: 'chat', label: 'Research Assistant', icon: MessageSquare },
    { id: 'sources', label: 'Source Library', icon: BookOpen },
    { id: 'about', label: 'Methodology & Ethics', icon: ShieldCheck },
  ];

  // Admin Console tab is ONLY added if user is authenticated and is an admin
  if (user?.isAdmin || user?.role === 'admin') {
    navItems.push({ id: 'admin', label: 'Admin Console', icon: Database, isAdminOnly: true });
  }

  return (
    <>
      <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            
            {/* Brand Logo & Tag */}
            <div 
              className="flex items-center gap-3 cursor-pointer select-none"
              onClick={() => setActiveTab('landing')}
            >
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-slate-900 via-blue-900 to-blue-700 flex items-center justify-center text-white shadow-sm ring-1 ring-slate-900/10">
                <Scale className="w-5 h-5 text-sky-300" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-bold text-lg tracking-tight text-slate-900">LawForce</span>
                  <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
                    Pak Legal RAG
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 hidden sm:block">
                  Verified Pakistani Legal Corpus
                </p>
              </div>
            </div>

            {/* Navigation Tabs */}
            <nav className="hidden md:flex items-center gap-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-all ${
                      isActive
                        ? item.isAdminOnly
                          ? 'bg-purple-900 text-white shadow-sm'
                          : 'bg-slate-900 text-white shadow-sm'
                        : item.isAdminOnly
                          ? 'text-purple-700 hover:bg-purple-50 font-semibold'
                          : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                    }`}
                  >
                    <Icon className={`w-4 h-4 ${isActive ? 'text-sky-300' : item.isAdminOnly ? 'text-purple-600' : 'text-slate-400'}`} />
                    {item.label}
                    {item.isAdminOnly && (
                      <span className="text-[9px] font-bold px-1.5 py-0.2 bg-purple-200 text-purple-900 rounded">
                        Admin
                      </span>
                    )}
                  </button>
                );
              })}
            </nav>

            {/* Right Side: Corpus Badge & User Auth */}
            <div className="flex items-center gap-3">
              <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                500 Verified PDFs
              </div>

              {user ? (
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 border border-slate-200 text-xs text-slate-700 font-medium">
                    <UserCheck className="w-3.5 h-3.5 text-blue-600" />
                    <span className="max-w-[110px] truncate">{user.fullName || user.email}</span>
                    {user.isAdmin && (
                      <span className="text-[9px] font-extrabold uppercase px-1.5 py-0.2 bg-purple-100 text-purple-800 border border-purple-200 rounded">
                        Admin
                      </span>
                    )}
                  </div>
                  <button
                    onClick={logout}
                    title="Sign Out"
                    className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition cursor-pointer"
                  >
                    <LogOut className="w-4 h-4" />
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setShowAuthModal(true)}
                  className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-blue-600 text-white text-xs font-semibold hover:bg-blue-700 shadow-sm transition cursor-pointer"
                >
                  <Lock className="w-3.5 h-3.5" />
                  Sign In
                </button>
              )}
            </div>

          </div>
        </div>

        {/* Mobile Navigation Bar */}
        <div className="md:hidden flex items-center justify-around border-t border-slate-200 bg-slate-50 py-2 px-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex flex-col items-center gap-1 px-2 py-1 rounded text-[11px] font-medium transition ${
                  isActive ? 'text-blue-700 font-bold' : 'text-slate-500'
                }`}
              >
                <Icon className="w-4 h-4" />
                {item.label.split(' ')[0]}
              </button>
            );
          })}
        </div>
      </header>

      {/* Auth Modal */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
      />
    </>
  );
}
