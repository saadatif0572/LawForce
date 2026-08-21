import React, { useState, useEffect } from 'react';
import { 
  Search, Filter, BookOpen, ExternalLink, ShieldCheck, CheckCircle2, 
  FileText, Landmark, Scale, Calendar, FileCode, ChevronRight, X
} from 'lucide-react';
import { fetchApi } from '../api/client';

export default function SourcesPage() {
  const [sources, setSources] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [isLoading, setIsLoading] = useState(false);

  // Filter states
  const [searchQuery, setSearchQuery] = useState('');
  const [jurisdiction, setJurisdiction] = useState('');
  const [province, setProvince] = useState('');
  const [documentType, setDocumentType] = useState('');
  const [legalStatus, setLegalStatus] = useState('');

  // Detail Modal
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [modalLoading, setModalLoading] = useState(false);

  useEffect(() => {
    loadSources();
  }, [page, jurisdiction, province, documentType, legalStatus]);

  const loadSources = async () => {
    try {
      setIsLoading(true);
      const params = new URLSearchParams();
      params.append('page', page);
      params.append('limit', 25);
      if (searchQuery) params.append('search', searchQuery);
      if (jurisdiction) params.append('jurisdiction', jurisdiction);
      if (province) params.append('province', province);
      if (documentType) params.append('document_type', documentType);
      if (legalStatus) params.append('legal_status', legalStatus);

      const data = await fetchApi(`/api/v1/sources?${params.toString()}`);
      if (data) {
        setSources(data.sources || []);
        setTotalCount(data.total || 0);
        setTotalPages(data.total_pages || 1);
      }
    } catch (e) {
      console.error('Error fetching sources:', e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    loadSources();
  };

  const openDocumentModal = async (docId) => {
    try {
      setModalLoading(true);
      const data = await fetchApi(`/api/v1/sources/${docId}`);
      setSelectedDoc(data);
    } catch (e) {
      console.error('Error fetching document details:', e);
    } finally {
      setModalLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      
      {/* Header & Stats Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 legal-heading flex items-center gap-2.5">
            <BookOpen className="w-7 h-7 text-blue-700" />
            Verified Legal Source Registry
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Browse and inspect all 500 officially registered, checksum-verified Pakistani legal instruments.
          </p>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold self-start sm:self-auto">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          <span>{totalCount} Verified Documents Registered</span>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-4">
        <form onSubmit={handleSearchSubmit} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
            <input
              type="text"
              placeholder="Search by statute name (e.g. Penal Code, Civil Procedure, Constitution, Family Courts)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 text-xs bg-slate-50 border border-slate-300 rounded-lg focus:bg-white focus:ring-2 focus:ring-blue-600 focus:outline-none"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-lg shadow-xs transition cursor-pointer"
          >
            Search
          </button>
        </form>

        {/* Dropdown Filters */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          
          <div>
            <label className="block text-[11px] font-semibold text-slate-500 mb-1">Jurisdiction</label>
            <select
              value={jurisdiction}
              onChange={(e) => { setJurisdiction(e.target.value); setPage(1); }}
              className="w-full p-2 bg-slate-50 border border-slate-300 rounded-lg focus:ring-1 focus:ring-blue-600 outline-none"
            >
              <option value="">All Jurisdictions</option>
              <option value="federal">Federal</option>
              <option value="provincial">Provincial</option>
            </select>
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-500 mb-1">Province</label>
            <select
              value={province}
              onChange={(e) => { setProvince(e.target.value); setPage(1); }}
              className="w-full p-2 bg-slate-50 border border-slate-300 rounded-lg focus:ring-1 focus:ring-blue-600 outline-none"
            >
              <option value="">All Provinces</option>
              <option value="punjab">Punjab</option>
              <option value="sindh">Sindh</option>
              <option value="khyber_pakhtunkhwa">Khyber Pakhtunkhwa</option>
              <option value="balochistan">Balochistan</option>
            </select>
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-500 mb-1">Document Type</label>
            <select
              value={documentType}
              onChange={(e) => { setDocumentType(e.target.value); setPage(1); }}
              className="w-full p-2 bg-slate-50 border border-slate-300 rounded-lg focus:ring-1 focus:ring-blue-600 outline-none"
            >
              <option value="">All Document Types</option>
              <option value="constitution">Constitution</option>
              <option value="act">Act of Parliament / Assembly</option>
              <option value="ordinance">Ordinance</option>
              <option value="rules">Rules & Regulations</option>
              <option value="judgment">Reported Judgment</option>
            </select>
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-500 mb-1">Legal Status</label>
            <select
              value={legalStatus}
              onChange={(e) => { setLegalStatus(e.target.value); setPage(1); }}
              className="w-full p-2 bg-slate-50 border border-slate-300 rounded-lg focus:ring-1 focus:ring-blue-600 outline-none"
            >
              <option value="">All Statuses</option>
              <option value="in_force">In Force</option>
              <option value="amended">Amended</option>
              <option value="repealed">Repealed</option>
            </select>
          </div>

        </div>
      </div>

      {/* Sources Grid / List */}
      {isLoading ? (
        <div className="py-20 text-center text-xs text-slate-400 animate-pulse">
          Loading verified legal instruments...
        </div>
      ) : sources.length === 0 ? (
        <div className="py-16 text-center bg-white rounded-xl border border-slate-200 text-slate-500 text-xs">
          No matching legal documents found for the selected criteria.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sources.map((doc) => (
            <div
              key={doc.document_id}
              onClick={() => openDocumentModal(doc.document_id)}
              className="bg-white rounded-xl border border-slate-200 p-4.5 flex flex-col justify-between hover:shadow-md hover:border-blue-300 transition-all cursor-pointer group"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between gap-2">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                    doc.jurisdiction === 'federal'
                      ? 'bg-blue-50 text-blue-800 border border-blue-200'
                      : 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                  }`}>
                    {doc.province ? `${doc.province.toUpperCase()} • ${doc.jurisdiction.toUpperCase()}` : doc.jurisdiction.toUpperCase()}
                  </span>

                  <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                    doc.legal_status === 'in_force'
                      ? 'bg-emerald-100 text-emerald-800'
                      : 'bg-amber-100 text-amber-800'
                  }`}>
                    {doc.legal_status.replace('_', ' ').toUpperCase()}
                  </span>
                </div>

                <h3 className="font-bold text-sm text-slate-900 group-hover:text-blue-700 transition line-clamp-2">
                  {doc.canonical_title}
                </h3>

                <p className="text-xs text-slate-500">
                  <strong>Authority:</strong> {doc.authority}
                </p>
              </div>

              <div className="pt-3 mt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
                <span>{doc.page_count} {doc.page_count === 1 ? 'Page' : 'Pages'}</span>
                <span className="text-blue-600 font-semibold flex items-center gap-1 group-hover:translate-x-0.5 transition">
                  Details <ChevronRight className="w-3.5 h-3.5" />
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination Bar */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between bg-white px-4 py-3 rounded-xl border border-slate-200 text-xs">
          <button
            disabled={page <= 1}
            onClick={() => setPage(prev => Math.max(1, prev - 1))}
            className="px-3 py-1.5 rounded bg-slate-100 disabled:opacity-40 font-medium hover:bg-slate-200 transition"
          >
            Previous
          </button>
          <span className="text-slate-600 font-medium">
            Page {page} of {totalPages} ({totalCount} total laws)
          </span>
          <button
            disabled={page >= totalPages}
            onClick={() => setPage(prev => Math.min(totalPages, prev + 1))}
            className="px-3 py-1.5 rounded bg-slate-100 disabled:opacity-40 font-medium hover:bg-slate-200 transition"
          >
            Next
          </button>
        </div>
      )}

      {/* Document Detail Inspector Modal */}
      {selectedDoc && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6 border border-slate-200 animate-in fade-in zoom-in-95 duration-150 space-y-5">
            
            {/* Modal Header */}
            <div className="flex items-start justify-between gap-4 pb-4 border-b border-slate-200">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
                  {selectedDoc.document_type.toUpperCase()} • {selectedDoc.jurisdiction.toUpperCase()}
                </span>
                <h2 className="text-lg font-bold text-slate-900 mt-2">
                  {selectedDoc.canonical_title}
                </h2>
              </div>
              <button
                onClick={() => setSelectedDoc(null)}
                className="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Metadata Table */}
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-slate-400 font-semibold block mb-0.5">Enacting Authority</span>
                <span className="font-bold text-slate-800">{selectedDoc.authority}</span>
              </div>
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-slate-400 font-semibold block mb-0.5">Legal Status</span>
                <span className="font-bold text-emerald-700">{selectedDoc.legal_status.toUpperCase()}</span>
              </div>
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-slate-400 font-semibold block mb-0.5">Enactment Date</span>
                <span className="font-bold text-slate-800">{selectedDoc.enactment_date || 'N/A'}</span>
              </div>
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                <span className="text-slate-400 font-semibold block mb-0.5">Page Count</span>
                <span className="font-bold text-slate-800">{selectedDoc.page_count} Pages</span>
              </div>
            </div>

            {/* SHA-256 Checksum Provenance */}
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 space-y-1 text-xs">
              <span className="text-[11px] font-semibold text-slate-400 block">SHA-256 Cryptographic Checksum</span>
              <code className="text-[11px] font-mono text-slate-700 break-all select-all">
                {selectedDoc.content_sha256}
              </code>
            </div>

            {/* Official Source Link */}
            {selectedDoc.official_source_url && (
              <div className="pt-2 flex items-center justify-between">
                <a
                  href={selectedDoc.official_source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-lg shadow-xs transition"
                >
                  View Official Registry Gazette <ExternalLink className="w-3.5 h-3.5" />
                </a>
                <button
                  onClick={() => setSelectedDoc(null)}
                  className="px-4 py-2 text-xs font-medium text-slate-600 hover:bg-slate-100 rounded-lg"
                >
                  Close
                </button>
              </div>
            )}

          </div>
        </div>
      )}

    </div>
  );
}
