import React, { useState } from 'react';
import { AuthProvider, useAuth } from './features/auth/AuthContext';
import Navbar from './components/Navbar';
import DisclaimerBanner from './components/DisclaimerBanner';
import Footer from './components/Footer';
import LandingPage from './pages/LandingPage';
import ChatPage from './pages/ChatPage';
import SourcesPage from './pages/SourcesPage';
import AboutPage from './pages/AboutPage';
import AdminPage from './pages/AdminPage';
import { ShieldAlert, ArrowLeft, Lock } from 'lucide-react';

function AppContent() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('landing');
  const [prefilledQuery, setPrefilledQuery] = useState('');

  const handleSelectQueryFromLanding = (queryText) => {
    setPrefilledQuery(queryText);
    setActiveTab('chat');
  };

  const isAdmin = user?.isAdmin || user?.role === 'admin';

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 font-sans antialiased selection:bg-blue-100 selection:text-blue-900">
      
      {/* Navigation Bar */}
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      {/* Legal Disclaimer Banner */}
      <DisclaimerBanner />

      {/* Tab Router Views */}
      <div className="flex-1 flex flex-col">
        {activeTab === 'landing' && (
          <LandingPage 
            setActiveTab={setActiveTab} 
            onSelectQuery={handleSelectQueryFromLanding} 
          />
        )}

        {activeTab === 'chat' && (
          <ChatPage 
            initialQuery={prefilledQuery}
            onClearInitialQuery={() => setPrefilledQuery('')}
            setActiveTab={setActiveTab}
          />
        )}

        {activeTab === 'sources' && (
          <SourcesPage />
        )}

        {activeTab === 'about' && (
          <AboutPage />
        )}

        {activeTab === 'admin' && (
          isAdmin ? (
            <AdminPage />
          ) : (
            <div className="max-w-md mx-auto my-auto py-20 text-center space-y-4 bg-white p-8 rounded-2xl border border-slate-200 shadow-sm mt-12 mb-12">
              <div className="w-14 h-14 rounded-2xl bg-purple-50 border border-purple-200 text-purple-700 mx-auto flex items-center justify-center">
                <ShieldAlert className="w-7 h-7" />
              </div>
              <h2 className="text-xl font-bold text-slate-900">Administrator Access Restricted</h2>
              <p className="text-xs text-slate-500 leading-relaxed">
                The Ingestion & Corpus Administration console is restricted exclusively to authorized administrators.
              </p>
              <button
                onClick={() => setActiveTab('landing')}
                className="inline-flex items-center gap-2 px-4 py-2 bg-slate-900 text-white rounded-xl text-xs font-semibold hover:bg-slate-800 transition cursor-pointer"
              >
                <ArrowLeft className="w-3.5 h-3.5" /> Return to Home
              </button>
            </div>
          )
        )}
      </div>

      {/* Persistent Footer (Hidden in full-height chat workspace) */}
      {activeTab !== 'chat' && (
        <Footer setActiveTab={setActiveTab} />
      )}

    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
