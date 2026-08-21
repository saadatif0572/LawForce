import React from 'react';
import { 
  Scale, MessageSquare, BookOpen, ShieldCheck, CheckCircle2, 
  ArrowRight, Search, FileText, Landmark, FileCheck, Layers, HelpCircle
} from 'lucide-react';

export default function LandingPage({ setActiveTab, onSelectQuery }) {
  const categories = [
    {
      title: 'Constitutional Rights & Writs',
      icon: Landmark,
      color: 'from-blue-600 to-indigo-700',
      description: 'Articles 199 writ jurisdiction, Fundamental Rights (Articles 8-28), Article 184(3) public interest litigation.',
      sample: 'What is the scope of Habeas Corpus writ under Article 199 of the Constitution of Pakistan?'
    },
    {
      title: 'Criminal Law & Procedure',
      icon: Scale,
      color: 'from-slate-700 to-slate-900',
      description: 'Pakistan Penal Code offences, Section 302 Qatl-i-amd, CrPC Sections 497/498 bail principles and FIR procedure.',
      sample: 'What are the statutory conditions for grant of pre-arrest bail under Section 498 CrPC?'
    },
    {
      title: 'Civil & Specific Relief',
      icon: FileText,
      color: 'from-sky-600 to-blue-700',
      description: 'Code of Civil Procedure 1908, Order 39 temporary injunctions, Section 42 Specific Relief Act declaratory suits.',
      sample: 'What are the three essential ingredients for granting temporary injunction under Order 39 Rules 1 & 2 CPC?'
    },
    {
      title: 'Family & Succession Law',
      icon: Layers,
      color: 'from-emerald-600 to-teal-800',
      description: 'Family Courts Act 1964, Muslim Family Laws Ordinance 1961, Khula, Dower, child custody, and Succession Certificates.',
      sample: 'Explain the procedure for obtaining Khula and recovery of dower under the Family Courts Act 1964.'
    },
    {
      title: 'Cybercrime & Technology',
      icon: ShieldCheck,
      color: 'from-violet-600 to-purple-800',
      description: 'PECA 2016 Section 20 online harassment, digital evidence chain of custody, FIA cybercrime jurisdiction.',
      sample: 'What are the penalties for online defamation and unauthorized access under PECA 2016 Section 20?'
    },
    {
      title: 'Provincial Laws & Tenancy',
      icon: BookOpen,
      color: 'from-amber-600 to-orange-700',
      description: 'Punjab, Sindh, KP and Balochistan Land Revenue, Tenancy, Consumer Protection, and Local Government Acts.',
      sample: 'What is the crop-sharing (Batai) ratio and tenant protection under the Sindh Tenancy Act 1950?'
    }
  ];

  const handleQueryClick = (sampleQuery) => {
    if (onSelectQuery) {
      onSelectQuery(sampleQuery);
    }
    setActiveTab('chat');
  };

  return (
    <div className="space-y-16 pb-20">
      
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-white via-slate-50 to-blue-50/40 pt-12 pb-20 border-b border-slate-200">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 text-center space-y-6">
          
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-200 text-blue-800 text-xs font-semibold shadow-xs">
            <ShieldCheck className="w-3.5 h-3.5 text-blue-600" />
            <span>Grounded in 500 Verified Pakistani Legal Documents</span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-slate-900 legal-heading">
            AI-Powered Legal Research Grounded in <span className="text-blue-700">Pakistani Law</span>
          </h1>

          <p className="text-base sm:text-lg text-slate-600 max-w-3xl mx-auto leading-relaxed">
            Query federal acts, constitutional articles, provincial statutes, and reported Supreme Court precedents in plain English or Urdu. Receive rigorously cited, zero-hallucination legal analysis.
          </p>

          {/* Call to Actions */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
            <button
              onClick={() => setActiveTab('chat')}
              className="w-full sm:w-auto flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-sm shadow-md transition-all hover:ring-4 hover:ring-slate-900/10 cursor-pointer"
            >
              <MessageSquare className="w-4 h-4 text-sky-400" />
              Launch Research Assistant
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              onClick={() => setActiveTab('sources')}
              className="w-full sm:w-auto flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-white hover:bg-slate-50 text-slate-800 border border-slate-300 font-semibold text-sm shadow-xs transition cursor-pointer"
            >
              <BookOpen className="w-4 h-4 text-blue-600" />
              Browse 500-PDF Corpus
            </button>
          </div>

          {/* Trust Metrics Bar */}
          <div className="pt-8 grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-4xl mx-auto">
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
              <div className="text-2xl font-extrabold text-slate-900">500</div>
              <div className="text-xs text-slate-500 font-medium mt-0.5">Verified PDF Originals</div>
            </div>
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
              <div className="text-2xl font-extrabold text-blue-700">100%</div>
              <div className="text-xs text-slate-500 font-medium mt-0.5">SHA-256 Checksum Verified</div>
            </div>
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
              <div className="text-2xl font-extrabold text-slate-900">5 Provinces</div>
              <div className="text-xs text-slate-500 font-medium mt-0.5">Federal + 4 Provincial Codes</div>
            </div>
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
              <div className="text-2xl font-extrabold text-emerald-700">Bilingual</div>
              <div className="text-xs text-slate-500 font-medium mt-0.5">English & Urdu QA</div>
            </div>
          </div>

        </div>
      </section>

      {/* Query Categories Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 legal-heading">
            Comprehensive Statutory & Judicial Coverage
          </h2>
          <p className="text-sm text-slate-600">
            Explore key areas of Pakistani law with instant access to authentic statutory sections and reported rulings.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {categories.map((cat, idx) => {
            const Icon = cat.icon;
            return (
              <div
                key={idx}
                className="bg-white rounded-xl border border-slate-200 p-6 flex flex-col justify-between hover:shadow-md transition-all group"
              >
                <div className="space-y-3">
                  <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${cat.color} flex items-center justify-center text-white shadow-xs`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <h3 className="text-base font-bold text-slate-900 group-hover:text-blue-700 transition">
                    {cat.title}
                  </h3>
                  <p className="text-xs text-slate-500 leading-relaxed">
                    {cat.description}
                  </p>
                </div>

                <div className="pt-4 mt-4 border-t border-slate-100">
                  <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                    Example Query:
                  </div>
                  <button
                    onClick={() => handleQueryClick(cat.sample)}
                    className="w-full text-left text-xs font-medium text-blue-700 hover:text-blue-900 bg-blue-50/70 hover:bg-blue-100/70 p-2.5 rounded-lg transition flex items-center justify-between group/btn cursor-pointer"
                  >
                    <span className="line-clamp-2">{cat.sample}</span>
                    <ArrowRight className="w-3.5 h-3.5 shrink-0 ml-1.5 text-blue-600 group-hover/btn:translate-x-0.5 transition" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* RAG Grounding Architecture Highlights */}
      <section className="bg-slate-900 text-white py-16">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
          
          <div className="text-center max-w-2xl mx-auto space-y-2">
            <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-white legal-heading">
              Why LawForce Delivers Grounded Answers
            </h2>
            <p className="text-xs sm:text-sm text-slate-400">
              Unlike generic AI models that hallucinate case laws and sections, LawForce operates under an explicit multi-stage RAG pipeline.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-slate-800/80 p-6 rounded-xl border border-slate-700 space-y-3">
              <div className="w-8 h-8 rounded bg-blue-500/20 text-sky-400 flex items-center justify-center font-bold text-sm">
                1
              </div>
              <h3 className="font-bold text-base text-white">Hybrid Retrieval Engine</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Combines 1024-dimensional dense semantic vectors with sparse lexical matchers to retrieve exact statutory numbers (e.g. Article 199, Section 302 PPC, CrPC 497) across 500 legal PDFs.
              </p>
            </div>

            <div className="bg-slate-800/80 p-6 rounded-xl border border-slate-700 space-y-3">
              <div className="w-8 h-8 rounded bg-blue-500/20 text-sky-400 flex items-center justify-center font-bold text-sm">
                2
              </div>
              <h3 className="font-bold text-base text-white">Strict Legal Grounding</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                The Groq LLM is strictly constrained to synthesize answers only from the retrieved chunks, citing official statute titles, sections, jurisdictions, and page numbers.
              </p>
            </div>

            <div className="bg-slate-800/80 p-6 rounded-xl border border-slate-700 space-y-3">
              <div className="w-8 h-8 rounded bg-blue-500/20 text-sky-400 flex items-center justify-center font-bold text-sm">
                3
              </div>
              <h3 className="font-bold text-base text-white">Refusal & Clarity Safeguards</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                If the verified corpus does not contain reliable provisions for a question, LawForce explicitly states the limitation instead of generating false citations.
              </p>
            </div>
          </div>

          <div className="text-center pt-4">
            <button
              onClick={() => setActiveTab('about')}
              className="inline-flex items-center gap-2 text-xs font-semibold text-sky-400 hover:text-sky-300 transition"
            >
              Read full Technical Methodology & Ethics Report <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

        </div>
      </section>

    </div>
  );
}
