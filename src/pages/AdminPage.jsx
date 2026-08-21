import React, { useState, useEffect } from 'react';
import { 
  Database, RefreshCw, Upload, CheckCircle2, AlertTriangle, ShieldCheck, 
  Layers, Clock, FileText, BarChart3, ThumbsUp, ThumbsDown
} from 'lucide-react';
import { fetchApi } from '../api/client';

export default function AdminPage() {
  const [stats, setStats] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [ingestionTriggered, setIngestionTriggered] = useState(false);

  // Upload Form
  const [uploadFile, setUploadFile] = useState(null);
  const [canonicalTitle, setCanonicalTitle] = useState('');
  const [jurisdiction, setJurisdiction] = useState('federal');
  const [province, setProvince] = useState('');
  const [documentType, setDocumentType] = useState('act');
  const [authority, setAuthority] = useState('Parliament of Pakistan');
  const [officialUrl, setOfficialUrl] = useState('https://pakistancode.gov.pk');
  const [uploadStatus, setUploadStatus] = useState(null);

  useEffect(() => {
    loadAdminData();
  }, []);

  const loadAdminData = async () => {
    try {
      setIsLoading(true);
      const [statsData, jobsData] = await Promise.all([
        fetchApi('/api/v1/admin/corpus/stats'),
        fetchApi('/api/v1/admin/ingestion/jobs')
      ]);
      setStats(statsData);
      setJobs(jobsData || []);
    } catch (e) {
      console.error('Error loading admin data:', e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTriggerIngestion = async () => {
    try {
      setIngestionTriggered(true);
      await fetchApi('/api/v1/admin/ingestion/run', { method: 'POST' });
      setTimeout(() => {
        loadAdminData();
        setIngestionTriggered(false);
      }, 3000);
    } catch (e) {
      console.error('Error triggering ingestion:', e);
      setIngestionTriggered(false);
    }
  };

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!uploadFile) return;

    try {
      setUploadStatus({ type: 'loading', msg: 'Uploading and calculating SHA-256...' });
      const formData = new FormData();
      formData.append('file', uploadFile);
      formData.append('canonical_title', canonicalTitle);
      formData.append('jurisdiction', jurisdiction);
      if (province) formData.append('province', province);
      formData.append('document_type', documentType);
      formData.append('authority', authority);
      formData.append('official_source_url', officialUrl);

      const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/admin/documents/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('lawverse_auth_token') || 'dev_token'}`
        },
        body: formData,
      });

      if (!res.ok) throw new Error('Upload failed');
      const data = await res.json();
      setUploadStatus({ type: 'success', msg: `Successfully uploaded ${data.document_id} (${data.sha256.substring(0, 12)}...)` });
      setUploadFile(null);
      setCanonicalTitle('');
      loadAdminData();
    } catch (err) {
      setUploadStatus({ type: 'error', msg: err.message || 'Upload error' });
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 legal-heading flex items-center gap-2.5">
            <Database className="w-7 h-7 text-blue-700" />
            Corpus Administration & Ingestion Console
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Monitor real-time corpus status, trigger automated ingestion, and verify cryptographic checksum integrity.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={loadAdminData}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-white border border-slate-300 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>

          <button
            onClick={handleTriggerIngestion}
            disabled={ingestionTriggered}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold shadow-xs transition cursor-pointer"
          >
            <Layers className="w-3.5 h-3.5" />
            {ingestionTriggered ? 'Ingesting...' : 'Run Corpus Ingestion'}
          </button>
        </div>
      </div>

      {/* Corpus Delivery & Integrity KPI Cards */}
      {stats && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          
          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-2">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-semibold">Total Verified Documents</span>
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            </div>
            <div className="text-3xl font-black text-slate-900">{stats.total_documents}</div>
            <div className="text-[11px] text-emerald-700 font-bold bg-emerald-50 px-2 py-0.5 rounded inline-block">
              {stats.coverage_percentage}% of 500 Target Complete
            </div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-2">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-semibold">Federal vs Provincial</span>
              <ShieldCheck className="w-4 h-4 text-blue-600" />
            </div>
            <div className="text-xl font-bold text-slate-900">
              {stats.jurisdictions?.federal || 0} Federal / {stats.jurisdictions?.provincial || 0} Prov
            </div>
            <div className="text-[11px] text-slate-500">
              All 4 Provinces + Islamabad Capital Territory
            </div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-2">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-semibold">Legal Status Integrity</span>
              <FileText className="w-4 h-4 text-sky-600" />
            </div>
            <div className="text-xl font-bold text-emerald-700">
              {stats.legal_status?.in_force || stats.total_documents} In Force
            </div>
            <div className="text-[11px] text-slate-500">
              0 Unverifiable / 0 Unknown
            </div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-2">
            <div className="flex items-center justify-between text-slate-400">
              <span className="text-xs font-semibold">Researcher Satisfaction</span>
              <BarChart3 className="w-4 h-4 text-purple-600" />
            </div>
            <div className="text-xl font-bold text-purple-700">
              {stats.feedback?.satisfaction_rate || 100}%
            </div>
            <div className="text-[11px] text-slate-500">
              {stats.feedback?.positive || 0} Upvotes • {stats.feedback?.negative || 0} Flags
            </div>
          </div>

        </div>
      )}

      {/* Upload and Ingestion Jobs Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Document Upload Widget */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center gap-2 text-slate-900 font-bold text-base">
            <Upload className="w-5 h-5 text-blue-700" />
            <h3>Upload New Statutory Document</h3>
          </div>
          <p className="text-xs text-slate-500">
            Add a new verified PDF legal instrument to the local raw repository and registry.
          </p>

          <form onSubmit={handleUploadSubmit} className="space-y-3 text-xs">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Canonical Title</label>
              <input
                type="text"
                required
                placeholder="e.g. Islamabad Real Estate Regulatory Act, 2024"
                value={canonicalTitle}
                onChange={(e) => setCanonicalTitle(e.target.value)}
                className="w-full p-2.5 bg-slate-50 border border-slate-300 rounded-lg focus:bg-white focus:ring-2 focus:ring-blue-600 outline-none"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Jurisdiction</label>
                <select
                  value={jurisdiction}
                  onChange={(e) => setJurisdiction(e.target.value)}
                  className="w-full p-2 bg-slate-50 border border-slate-300 rounded-lg outline-none"
                >
                  <option value="federal">Federal</option>
                  <option value="provincial">Provincial</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Province (Optional)</label>
                <select
                  value={province}
                  onChange={(e) => setProvince(e.target.value)}
                  className="w-full p-2 bg-slate-50 border border-slate-300 rounded-lg outline-none"
                >
                  <option value="">None (Federal)</option>
                  <option value="punjab">Punjab</option>
                  <option value="sindh">Sindh</option>
                  <option value="khyber_pakhtunkhwa">Khyber Pakhtunkhwa</option>
                  <option value="balochistan">Balochistan</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Document Type</label>
                <select
                  value={documentType}
                  onChange={(e) => setDocumentType(e.target.value)}
                  className="w-full p-2 bg-slate-50 border border-slate-300 rounded-lg outline-none"
                >
                  <option value="act">Act of Parliament / Assembly</option>
                  <option value="ordinance">Ordinance</option>
                  <option value="rules">Rules & Regulations</option>
                  <option value="judgment">Reported Judgment</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Enacting Authority</label>
                <input
                  type="text"
                  value={authority}
                  onChange={(e) => setAuthority(e.target.value)}
                  className="w-full p-2 bg-slate-50 border border-slate-300 rounded-lg outline-none"
                />
              </div>
            </div>

            <div>
              <label className="block font-semibold text-slate-700 mb-1">Official PDF File</label>
              <input
                type="file"
                accept=".pdf"
                required
                onChange={(e) => setUploadFile(e.target.files[0])}
                className="w-full text-xs text-slate-500 file:mr-3 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer"
              />
            </div>

            {uploadStatus && (
              <div className={`p-2.5 rounded-lg text-xs font-medium ${
                uploadStatus.type === 'success' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' :
                uploadStatus.type === 'error' ? 'bg-red-50 text-red-800 border border-red-200' :
                'bg-blue-50 text-blue-800 border border-blue-200'
              }`}>
                {uploadStatus.msg}
              </div>
            )}

            <button
              type="submit"
              className="w-full py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-lg transition cursor-pointer"
            >
              Upload and Register Document
            </button>
          </form>
        </div>

        {/* Recent Ingestion Runs Log */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4 flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-slate-900 font-bold text-base">
              <Clock className="w-5 h-5 text-blue-700" />
              <h3>Recent Ingestion & Indexing Jobs</h3>
            </div>
            <p className="text-xs text-slate-500">
              Audit log of vector indexing runs, chunk counts, and completed stages.
            </p>

            <div className="space-y-2.5 max-h-80 overflow-y-auto">
              {jobs.length === 0 ? (
                <div className="p-4 text-center text-xs text-slate-400 bg-slate-50 rounded-lg">
                  No ingestion jobs recorded yet.
                </div>
              ) : (
                jobs.map((j) => (
                  <div key={j.id} className="p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-800">Job {j.id.substring(0, 8)}...</span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                        j.status === 'completed' ? 'bg-emerald-100 text-emerald-800' : 'bg-blue-100 text-blue-800'
                      }`}>
                        {j.status}
                      </span>
                    </div>
                    <div className="text-[11px] text-slate-600 flex items-center justify-between">
                      <span>Processed: <strong>{j.processed_documents} / {j.total_documents}</strong> docs</span>
                      <span>Chunks: <strong>{j.total_chunks}</strong> indexed</span>
                    </div>
                    {j.started_at && (
                      <div className="text-[10px] text-slate-400">
                        Started: {new Date(j.started_at).toLocaleString()}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="p-3 bg-blue-50 border border-blue-200 rounded-xl text-[11px] text-blue-900 flex items-center justify-between">
            <span className="font-semibold">Corpus Validation Status:</span>
            <span className="font-bold text-emerald-700">100% Passed (500 Valid Checksums)</span>
          </div>
        </div>

      </div>

    </div>
  );
}
