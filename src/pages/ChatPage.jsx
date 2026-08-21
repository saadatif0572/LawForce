import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { 
  Send, Plus, Trash2, MessageSquare, Scale, BookOpen, ExternalLink, 
  Copy, Check, ThumbsUp, ThumbsDown, AlertTriangle, ShieldCheck, 
  Globe, Filter, Sparkles, ChevronDown, ChevronUp, Clock, Info, Lock, LogIn
} from 'lucide-react';
import { fetchApi, streamLegalQuery } from '../api/client';
import { useAuth } from '../features/auth/AuthContext';
import AuthModal from '../components/AuthModal';

export default function ChatPage({ initialQuery, onClearInitialQuery, setActiveTab }) {
  const { user } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);

  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState(initialQuery || '');
  const [isLoading, setIsLoading] = useState(false);
  const [language, setLanguage] = useState('en');
  const [jurisdiction, setJurisdiction] = useState('all');
  
  // UI states
  const [copiedMsgId, setCopiedMsgId] = useState(null);
  const [expandedSources, setExpandedSources] = useState({});
  const [feedbackModalMsgId, setFeedbackModalMsgId] = useState(null);
  const [feedbackRating, setFeedbackRating] = useState(1);
  const [feedbackComments, setFeedbackComments] = useState('');
  const [feedbackSubmitted, setFeedbackSubmitted] = useState({});

  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (user) {
      loadSessions();
    } else {
      setSessions([]);
      setMessages([]);
    }
  }, [user]);

  useEffect(() => {
    if (initialQuery) {
      setInputText(initialQuery);
      onClearInitialQuery && onClearInitialQuery();
    }
  }, [initialQuery]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadSessions = async () => {
    try {
      const data = await fetchApi('/api/v1/chats');
      setSessions(data || []);
    } catch (e) {
      console.warn('Could not fetch sessions list:', e);
    }
  };

  const handleSelectSession = async (chatId) => {
    try {
      setIsLoading(true);
      setCurrentSessionId(chatId);
      const data = await fetchApi(`/api/v1/chats/${chatId}`);
      if (data && data.messages) {
        setMessages(data.messages);
        setLanguage(data.language || 'en');
        setJurisdiction(data.jurisdiction_filter || 'all');
      }
    } catch (e) {
      console.error('Error loading session messages:', e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    setCurrentSessionId(null);
    setMessages([]);
    setInputText('');
  };

  const handleDeleteSession = async (e, chatId) => {
    e.stopPropagation();
    try {
      await fetchApi(`/api/v1/chats/${chatId}`, { method: 'DELETE' });
      setSessions(prev => prev.filter(s => s.id !== chatId));
      if (currentSessionId === chatId) {
        handleNewChat();
      }
    } catch (e) {
      console.error('Error deleting session:', e);
    }
  };

  const handleSend = async (e) => {
    e?.preventDefault();
    if (!user) {
      setShowAuthModal(true);
      return;
    }

    const query = inputText.trim();
    if (!query || isLoading) return;

    const userMsgId = 'usr_' + Date.now();
    const assistantMsgId = 'ast_' + Date.now();

    const newUserMsg = {
      id: userMsgId,
      role: 'user',
      content: query,
      created_at: new Date().toISOString()
    };

    const initialAssistantMsg = {
      id: assistantMsgId,
      role: 'assistant',
      content: '',
      confidence: 'medium',
      needs_clarification: false,
      disclaimer: 'General legal information only; not legal advice.',
      sources: [],
      created_at: new Date().toISOString()
    };

    setMessages(prev => [...prev, newUserMsg, initialAssistantMsg]);
    setInputText('');
    setIsLoading(true);

    let streamAccumulator = '';

    await streamLegalQuery({
      query,
      chatId: currentSessionId,
      jurisdiction,
      language,
      onToken: (token) => {
        streamAccumulator += token;
        setMessages(prev => prev.map(msg => 
          msg.id === assistantMsgId ? { ...msg, content: streamAccumulator } : msg
        ));
      },
      onDone: (finalData) => {
        setMessages(prev => prev.map(msg => 
          msg.id === assistantMsgId ? {
            ...msg,
            content: finalData.answer_markdown || streamAccumulator,
            confidence: finalData.confidence || 'medium',
            needs_clarification: finalData.needs_clarification || false,
            disclaimer: finalData.disclaimer || msg.disclaimer,
            sources: finalData.sources || []
          } : msg
        ));
        setIsLoading(false);
        loadSessions();
      },
      onError: (err) => {
        setMessages(prev => prev.map(msg => 
          msg.id === assistantMsgId ? {
            ...msg,
            content: `**Error processing query:** ${err.message || 'Server connection error'}. Please verify backend status.`,
            confidence: 'ungrounded'
          } : msg
        ));
        setIsLoading(false);
      }
    });
  };

  const handleCopyAnswer = (msgId, text) => {
    navigator.clipboard.writeText(text);
    setCopiedMsgId(msgId);
    setTimeout(() => setCopiedMsgId(null), 2000);
  };

  const toggleSources = (msgId) => {
    setExpandedSources(prev => ({ ...prev, [msgId]: !prev[msgId] }));
  };

  const handleOpenFeedback = (msgId, rating) => {
    setFeedbackModalMsgId(msgId);
    setFeedbackRating(rating);
    setFeedbackComments('');
  };

  const handleFeedbackSubmit = async (e) => {
    e.preventDefault();
    if (!feedbackModalMsgId) return;

    try {
      await fetchApi('/api/v1/feedback', {
        method: 'POST',
        body: JSON.stringify({
          message_id: feedbackModalMsgId,
          rating: feedbackRating,
          comments: feedbackComments,
        }),
      });
      setFeedbackSubmitted(prev => ({ ...prev, [feedbackModalMsgId]: true }));
      setFeedbackModalMsgId(null);
    } catch (e) {
      console.error('Error submitting feedback:', e);
      setFeedbackModalMsgId(null);
    }
  };

  const exampleQuestions = [
    { title: 'Pre-Arrest Bail', q: 'What are the grounds and principles for pre-arrest bail under Section 498 CrPC?' },
    { title: 'Article 199 Writs', q: 'Explain High Court writ jurisdiction and conditions for Habeas Corpus under Article 199.' },
    { title: 'Khula & Dower', q: 'What is the statutory procedure for obtaining Khula and recovery of dower under Family Courts Act 1964?' },
    { title: 'Cyber Defamation', q: 'What are the offences and penalties for online harassment under Section 20 PECA 2016?' },
    { title: 'Urdu Inquiry', q: 'تعزیرات پاکستان کی دفعہ 302 کے تحت قتل عمد کی کیا سزائیں ہیں؟' }
  ];

  return (
    <div className="flex h-[calc(100vh-64px)] overflow-hidden bg-slate-100">
      
      {/* Left Sidebar: Chat Sessions History */}
      <aside className="w-72 bg-white border-r border-slate-200 flex flex-col shrink-0 hidden lg:flex">
        
        <div className="p-3.5 border-b border-slate-200">
          <button
            onClick={() => {
              if (!user) {
                setShowAuthModal(true);
              } else {
                handleNewChat();
              }
            }}
            className="w-full flex items-center justify-center gap-2 px-3.5 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs shadow-xs transition cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            New Legal Inquiry
          </button>
        </div>

        {/* History List */}
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          <div className="px-2 py-1.5 text-[10px] font-bold tracking-wider text-slate-400 uppercase">
            Recent Research Sessions
          </div>

          {!user ? (
            <div className="px-3 py-8 text-center text-xs text-slate-400 space-y-2">
              <Lock className="w-5 h-5 mx-auto text-slate-300" />
              <p>Sign in to preserve and view your legal research history.</p>
            </div>
          ) : sessions.length === 0 ? (
            <div className="px-3 py-6 text-center text-xs text-slate-400">
              No previous chat history found.
            </div>
          ) : (
            sessions.map((s) => {
              const isSelected = currentSessionId === s.id;
              return (
                <div
                  key={s.id}
                  onClick={() => handleSelectSession(s.id)}
                  className={`group flex items-center justify-between px-3 py-2 rounded-lg text-xs cursor-pointer transition ${
                    isSelected
                      ? 'bg-blue-50 text-blue-900 font-semibold border border-blue-200'
                      : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                  }`}
                >
                  <div className="flex items-center gap-2 truncate pr-2">
                    <MessageSquare className={`w-3.5 h-3.5 shrink-0 ${isSelected ? 'text-blue-600' : 'text-slate-400'}`} />
                    <span className="truncate">{s.title || 'Untitled Research Query'}</span>
                  </div>
                  <button
                    onClick={(e) => handleDeleteSession(e, s.id)}
                    className="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-red-600 transition"
                    title="Delete Chat"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              );
            })
          )}
        </div>

        {/* Sidebar Footer */}
        <div className="p-3 border-t border-slate-200 bg-slate-50 text-[11px] text-slate-500 flex items-center justify-between">
          <span className="flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            500 PDFs Indexed
          </span>
          <button 
            onClick={() => setActiveTab('sources')}
            className="text-blue-600 hover:underline font-medium cursor-pointer"
          >
            View Corpus
          </button>
        </div>
      </aside>

      {/* Main Conversation Workspace */}
      <main className="flex-1 flex flex-col bg-slate-50 overflow-hidden relative">
        
        {/* Top Control Bar */}
        <div className="bg-white border-b border-slate-200 px-4 py-2.5 flex items-center justify-between gap-4 text-xs">
          <div className="flex items-center gap-3">
            <span className="font-bold text-slate-800 flex items-center gap-1.5">
              <Scale className="w-4 h-4 text-blue-700" />
              Pakistani Statutory RAG
            </span>
            <span className="hidden sm:inline-block text-slate-300">|</span>
            
            {/* Jurisdiction Selector */}
            <div className="flex items-center gap-1.5">
              <Filter className="w-3.5 h-3.5 text-slate-400" />
              <span className="text-slate-500 font-medium hidden sm:inline">Jurisdiction:</span>
              <select
                value={jurisdiction}
                onChange={(e) => setJurisdiction(e.target.value)}
                className="bg-slate-50 border border-slate-300 text-slate-700 text-xs rounded-md px-2 py-1 focus:ring-1 focus:ring-blue-600 outline-none cursor-pointer"
              >
                <option value="all">All Jurisdictions (Federal & Provincial)</option>
                <option value="federal">Federal Law Only</option>
                <option value="punjab">Punjab Laws</option>
                <option value="sindh">Sindh Laws</option>
                <option value="khyber_pakhtunkhwa">Khyber Pakhtunkhwa Laws</option>
                <option value="balochistan">Balochistan Laws</option>
              </select>
            </div>
          </div>

          {/* Language Toggle */}
          <div className="flex items-center gap-1.5 bg-slate-100 p-0.5 rounded-lg border border-slate-200">
            <button
              onClick={() => setLanguage('en')}
              className={`px-2 py-1 rounded text-[11px] font-bold transition cursor-pointer ${
                language === 'en' ? 'bg-white text-blue-800 shadow-xs' : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              English
            </button>
            <button
              onClick={() => setLanguage('ur')}
              className={`px-2 py-1 rounded text-[11px] font-bold transition cursor-pointer ${
                language === 'ur' ? 'bg-white text-blue-800 shadow-xs' : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              اردو (Urdu)
            </button>
          </div>
        </div>

        {/* Message Stream Area */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
          
          {!user ? (
            /* Mandatory Login Gate */
            <div className="max-w-md mx-auto my-auto py-16 text-center space-y-5 bg-white p-8 rounded-2xl border border-slate-200 shadow-sm">
              <div className="w-14 h-14 rounded-2xl bg-blue-50 border border-blue-200 text-blue-700 mx-auto flex items-center justify-center shadow-xs">
                <Lock className="w-7 h-7" />
              </div>
              <div className="space-y-2">
                <h2 className="text-xl font-bold text-slate-900 legal-heading">
                  Sign In Required
                </h2>
                <p className="text-xs text-slate-500 leading-relaxed">
                  To query verified Pakistani statutes, access case law precedents, and preserve your legal research sessions, please sign in or create an account.
                </p>
              </div>

              <div className="pt-2 flex flex-col gap-2">
                <button
                  onClick={() => setShowAuthModal(true)}
                  className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl shadow-xs transition flex items-center justify-center gap-2 cursor-pointer"
                >
                  <LogIn className="w-4 h-4" />
                  Sign In / Create Account
                </button>
                <button
                  onClick={() => setActiveTab('sources')}
                  className="w-full py-2.5 bg-slate-50 hover:bg-slate-100 text-slate-700 font-semibold text-xs rounded-xl border border-slate-200 transition cursor-pointer"
                >
                  Browse Public Source Registry
                </button>
              </div>

              <p className="text-[10px] text-slate-400 pt-2">
                Grounded in 500 Verified Pakistani Legal Instruments
              </p>
            </div>
          ) : messages.length === 0 ? (
            /* Calm Empty State */
            <div className="max-w-2xl mx-auto my-auto py-12 text-center space-y-6">
              <div className="w-12 h-12 rounded-2xl bg-blue-50 border border-blue-200 text-blue-700 mx-auto flex items-center justify-center shadow-xs">
                <Scale className="w-6 h-6" />
              </div>
              <div className="space-y-2">
                <h2 className="text-xl font-bold text-slate-900 legal-heading">
                  LawForce Legal Research Assistant
                </h2>
                <p className="text-xs text-slate-500 max-w-md mx-auto leading-relaxed">
                  Ask any question regarding the Constitution of Pakistan, Pakistan Penal Code, CrPC, CPC, Family Law, or Provincial enactments.
                </p>
              </div>

              {/* Example Prompts */}
              <div className="text-left space-y-2 max-w-xl mx-auto pt-2">
                <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 px-1">
                  Suggested Legal Inquiries:
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {exampleQuestions.map((eg, i) => (
                    <button
                      key={i}
                      onClick={() => { setInputText(eg.q); }}
                      className="p-3 bg-white hover:bg-blue-50/60 border border-slate-200 hover:border-blue-300 rounded-xl text-left transition group cursor-pointer"
                    >
                      <div className="font-semibold text-xs text-slate-800 group-hover:text-blue-700 flex items-center justify-between">
                        <span>{eg.title}</span>
                        <span className="text-[10px] text-blue-600 opacity-0 group-hover:opacity-100 transition">Use ↵</span>
                      </div>
                      <p className="text-[11px] text-slate-500 line-clamp-2 mt-1">
                        {eg.q}
                      </p>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            /* Messages List */
            messages.map((msg) => {
              const isUser = msg.role === 'user';
              const isUrdu = /[\u0600-\u06FF]/.test(msg.content);

              return (
                <div
                  key={msg.id}
                  className={`flex gap-3 max-w-4xl mx-auto ${isUser ? 'justify-end' : 'justify-start'}`}
                >
                  {!isUser && (
                    <div className="w-8 h-8 rounded-lg bg-slate-900 text-white flex items-center justify-center shrink-0 shadow-xs mt-1">
                      <Scale className="w-4 h-4 text-sky-300" />
                    </div>
                  )}

                  <div className={`space-y-2 max-w-[85%] sm:max-w-[78%] ${isUser ? 'items-end' : 'items-start'}`}>
                    
                    {/* Bubble Content */}
                    <div
                      className={`p-4 rounded-2xl text-xs sm:text-sm leading-relaxed shadow-xs ${
                        isUser
                          ? 'bg-blue-600 text-white rounded-tr-xs'
                          : 'bg-white border border-slate-200 text-slate-900 rounded-tl-xs'
                      }`}
                    >
                      <div className={`prose prose-xs sm:prose-sm max-w-none ${isUser ? 'text-white prose-invert' : 'text-slate-900'} ${isUrdu ? 'urdu-text' : ''}`}>
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {msg.content}
                        </ReactMarkdown>
                      </div>

                      {/* Disclaimer Footnote for Assistant */}
                      {!isUser && msg.disclaimer && (
                        <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-start gap-1.5 text-[11px] text-slate-400 italic">
                          <Info className="w-3 h-3 text-slate-400 shrink-0 mt-0.5" />
                          <span>{msg.disclaimer}</span>
                        </div>
                      )}
                    </div>

                    {/* Assistant Metadata & Source Citations */}
                    {!isUser && msg.content && (
                      <div className="space-y-2 w-full">
                        
                        {/* Action Bar */}
                        <div className="flex items-center justify-between text-xs text-slate-500 px-1">
                          
                          <div className="flex items-center gap-2">
                            {msg.confidence && (
                              <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                                msg.confidence === 'high'
                                  ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                                  : msg.confidence === 'medium'
                                  ? 'bg-blue-50 text-blue-700 border border-blue-200'
                                  : 'bg-amber-50 text-amber-700 border border-amber-200'
                              }`}>
                                {msg.confidence} confidence
                              </span>
                            )}

                            {msg.sources && msg.sources.length > 0 && (
                              <button
                                onClick={() => toggleSources(msg.id)}
                                className="flex items-center gap-1 text-[11px] font-semibold text-blue-700 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 px-2 py-0.5 rounded border border-blue-200 transition cursor-pointer"
                              >
                                <BookOpen className="w-3 h-3" />
                                {msg.sources.length} Cited Sources
                                {expandedSources[msg.id] ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                              </button>
                            )}
                          </div>

                          {/* Copy & Feedback */}
                          <div className="flex items-center gap-1">
                            <button
                              onClick={() => handleCopyAnswer(msg.id, msg.content)}
                              className="p-1.5 rounded-md hover:bg-slate-200 text-slate-500 hover:text-slate-800 transition cursor-pointer"
                              title="Copy Answer"
                            >
                              {copiedMsgId === msg.id ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                            </button>

                            <button
                              onClick={() => handleOpenFeedback(msg.id, 1)}
                              disabled={feedbackSubmitted[msg.id]}
                              className={`p-1.5 rounded-md hover:bg-slate-200 transition cursor-pointer ${
                                feedbackSubmitted[msg.id] ? 'text-emerald-600' : 'text-slate-500 hover:text-emerald-600'
                              }`}
                              title="Helpful"
                            >
                              <ThumbsUp className="w-3.5 h-3.5" />
                            </button>

                            <button
                              onClick={() => handleOpenFeedback(msg.id, -1)}
                              disabled={feedbackSubmitted[msg.id]}
                              className="p-1.5 rounded-md hover:bg-slate-200 text-slate-500 hover:text-red-600 transition cursor-pointer"
                              title="Needs Correction"
                            >
                              <ThumbsDown className="w-3.5 h-3.5" />
                            </button>
                          </div>

                        </div>

                        {/* Expandable Citations Drawer */}
                        {expandedSources[msg.id] && msg.sources && (
                          <div className="bg-white border border-slate-200 rounded-xl p-3 space-y-2.5 shadow-xs animate-in fade-in duration-150">
                            <div className="text-[11px] font-bold text-slate-700 uppercase tracking-wider flex items-center justify-between">
                              <span>Verified Citations & Statutory Links</span>
                              <span className="text-[10px] text-slate-400 font-normal">Official Sources</span>
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                              {msg.sources.map((src, idx) => (
                                <div key={idx} className="p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-xs space-y-1">
                                  <div className="font-bold text-slate-900 line-clamp-1">
                                    {src.title}
                                  </div>
                                  <div className="flex items-center justify-between text-[11px] text-slate-600">
                                    <span className="font-semibold text-blue-700">{src.article_or_section}</span>
                                    <span className="px-1.5 py-0.2 rounded bg-slate-200 text-[10px] font-medium uppercase">
                                      {src.jurisdiction}
                                    </span>
                                  </div>
                                  {src.source_url && (
                                    <a
                                      href={src.source_url}
                                      target="_blank"
                                      rel="noreferrer"
                                      className="inline-flex items-center gap-1 text-[10px] text-blue-600 hover:underline pt-1"
                                    >
                                      Official Registry <ExternalLink className="w-2.5 h-2.5" />
                                    </a>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                      </div>
                    )}

                  </div>
                </div>
              );
            })
          )}

          {isLoading && (
            <div className="flex gap-3 max-w-4xl mx-auto items-center text-xs text-slate-500 animate-pulse">
              <div className="w-8 h-8 rounded-lg bg-slate-900 text-white flex items-center justify-center">
                <Scale className="w-4 h-4 text-sky-300" />
              </div>
              <span>Searching verified Pakistani legal corpus and formulating grounded response...</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Composer */}
        <div className="bg-white border-t border-slate-200 p-4">
          <div className="max-w-4xl mx-auto">
            <form onSubmit={handleSend} className="relative flex items-center">
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onFocus={() => {
                  if (!user) setShowAuthModal(true);
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend(e);
                  }
                }}
                rows={2}
                placeholder={
                  !user
                    ? 'Please sign in to ask legal questions grounded in Pakistani law...'
                    : language === 'ur'
                    ? 'پاکستانی قانون کے بارے میں سوال درج کریں (جیسے: دفعہ 302، ضمانت کے اصول، آرٹیکل 199)...'
                    : 'Ask a legal question in plain English (e.g. grounds for pre-arrest bail under CrPC 498, Article 199 writ)...'
                }
                className={`w-full pr-14 pl-4 py-3 text-xs sm:text-sm bg-slate-50 border border-slate-300 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent resize-none leading-relaxed ${
                  language === 'ur' ? 'urdu-text' : ''
                }`}
              />
              <button
                type="submit"
                disabled={!inputText.trim() || isLoading}
                className="absolute right-2.5 p-2.5 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white shadow-sm transition cursor-pointer"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>

            <div className="flex items-center justify-between text-[11px] text-slate-400 mt-2 px-1">
              <span>Press <strong>Enter</strong> to send, <strong>Shift + Enter</strong> for new line</span>
              <span className="hidden sm:inline">Grounding: 500 Verified Pakistani Legal Documents</span>
            </div>
          </div>
        </div>

      </main>

      {/* Auth Modal Trigger */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
      />

      {/* Feedback Dialog Modal */}
      {feedbackModalMsgId && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6 border border-slate-200 animate-in fade-in zoom-in-95 duration-150">
            <h3 className="text-base font-bold text-slate-900 mb-2">
              {feedbackRating === 1 ? 'Positive Feedback' : 'Report Legal Discrepancy'}
            </h3>
            <p className="text-xs text-slate-500 mb-4">
              Help us refine the legal accuracy and grounding of LawForce assistant responses.
            </p>

            <form onSubmit={handleFeedbackSubmit} className="space-y-3">
              <textarea
                rows={3}
                required
                placeholder={feedbackRating === 1 ? 'What was particularly helpful?' : 'Please specify any statutory inaccuracies, citation errors, or missing context...'}
                value={feedbackComments}
                onChange={(e) => setFeedbackComments(e.target.value)}
                className="w-full p-3 text-xs rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-600"
              />

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setFeedbackModalMsgId(null)}
                  className="px-3.5 py-1.5 text-xs text-slate-600 hover:bg-slate-100 rounded-lg cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 text-xs font-bold bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer"
                >
                  Submit Feedback
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
