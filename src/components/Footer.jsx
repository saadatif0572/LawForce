import React from 'react';
import { Scale, ExternalLink, ShieldCheck, CheckCircle2 } from 'lucide-react';

export default function Footer({ setActiveTab }) {
  return (
    <footer className="bg-slate-900 text-slate-400 text-xs border-t border-slate-800 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          
          {/* Brand & Mission */}
          <div className="md:col-span-2 space-y-3">
            <div className="flex items-center gap-2 text-white font-bold text-base">
              <Scale className="w-5 h-5 text-sky-400" />
              <span>LawForce Pakistan</span>
            </div>
            <p className="text-slate-400 max-w-md leading-relaxed">
              State-of-the-art legal information retrieval and research platform grounded strictly in 500 verified Pakistani statutory enactments, gazetted rules, and landmark judicial decisions.
            </p>
            <div className="flex items-center gap-3 pt-2 text-[11px]">
              <span className="flex items-center gap-1 text-emerald-400 font-medium">
                <CheckCircle2 className="w-3.5 h-3.5" /> 500 Verified PDFs
              </span>
              <span className="text-slate-600">•</span>
              <span className="flex items-center gap-1 text-sky-400 font-medium">
                <ShieldCheck className="w-3.5 h-3.5" /> Zero-Hallucination Grounding
              </span>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="font-semibold text-slate-200 uppercase tracking-wider text-[11px] mb-3">Navigation</h4>
            <ul className="space-y-2">
              <li>
                <button onClick={() => setActiveTab('chat')} className="hover:text-white transition">
                  Research Assistant
                </button>
              </li>
              <li>
                <button onClick={() => setActiveTab('sources')} className="hover:text-white transition">
                  Source Registry & Catalog
                </button>
              </li>
              <li>
                <button onClick={() => setActiveTab('about')} className="hover:text-white transition">
                  RAG Architecture & Ethics
                </button>
              </li>
              <li>
                <button onClick={() => setActiveTab('admin')} className="hover:text-white transition">
                  Admin Verification Console
                </button>
              </li>
            </ul>
          </div>

          {/* Primary Legal Registries */}
          <div>
            <h4 className="font-semibold text-slate-200 uppercase tracking-wider text-[11px] mb-3">Official Sourced Portals</h4>
            <ul className="space-y-2 text-[11px]">
              <li>
                <a href="https://pakistancode.gov.pk" target="_blank" rel="noreferrer" className="flex items-center gap-1 hover:text-white transition">
                  Pakistan Code <ExternalLink className="w-3 h-3 text-slate-600" />
                </a>
              </li>
              <li>
                <a href="https://punjablaws.gov.pk" target="_blank" rel="noreferrer" className="flex items-center gap-1 hover:text-white transition">
                  Punjab Laws Online <ExternalLink className="w-3 h-3 text-slate-600" />
                </a>
              </li>
              <li>
                <a href="https://www.sindhlaws.gov.pk" target="_blank" rel="noreferrer" className="flex items-center gap-1 hover:text-white transition">
                  Sindh Code <ExternalLink className="w-3 h-3 text-slate-600" />
                </a>
              </li>
              <li>
                <a href="https://supremecourt.gov.pk" target="_blank" rel="noreferrer" className="flex items-center gap-1 hover:text-white transition">
                  Supreme Court of Pakistan <ExternalLink className="w-3 h-3 text-slate-600" />
                </a>
              </li>
            </ul>
          </div>

        </div>

        {/* Bottom Bar */}
        <div className="pt-6 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4 text-slate-500 text-[11px]">
          <p>© 2026 LawForce. All rights reserved. Strictly for research and educational purposes.</p>
          <p className="flex items-center gap-1">
            <span>Verified Corpus SHA-256 Checksums Enforced</span>
          </p>
        </div>
      </div>
    </footer>
  );
}
