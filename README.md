# LAWVERSE: Professional Pakistani Legal Research & Information Assistant

LAWVERSE is an elite, production-quality legal information and research platform grounded strictly in **500 verified Pakistani legal sources**. It enables legal researchers, advocates, students, and citizens to query federal enactments, constitutional articles, provincial codes, and reported Supreme Court precedents in plain **English** or **Urdu**, returning rigorously grounded legal analyses with official gazetted citations.

---

## 🏛️ System Architecture

```
                               ┌─────────────────────────────────────────┐
                               │   React 19 + Vite 8 + Tailwind CSS UI   │
                               └────────────────────┬────────────────────┘
                                                    │ REST & SSE Streaming
                                                    ▼
                               ┌─────────────────────────────────────────┐
                               │       FastAPI Backend (:8000)          │
                               │  - Supabase JWT Verification & RBAC     │
                               │  - Multi-page PDF Extraction & OCR      │
                               │  - Legal-Aware Hierarchy Chunker        │
                               └────────────────────┬────────────────────┘
                                                    │
                 ┌──────────────────────────────────┴──────────────────────────────────┐
                 ▼                                                                     ▼
   ┌───────────────────────────┐                                         ┌───────────────────────────┐
   │    Hybrid Retrieval       │                                         │    Grounded Generation    │
   │  - Qdrant Dense Vectors   │                                         │  - Direct Groq Python SDK │
   │  - Exact Section Lexical  │                                         │  - Strict Evidence Rules  │
   │  - Reciprocal Rank Fusion │                                         │  - Refusal Safeguards     │
   └─────────────┬─────────────┘                                         └─────────────┬─────────────┘
                 │                                                                     │
                 ▼                                                                     ▼
   ┌───────────────────────────┐                                         ┌───────────────────────────┐
   │ 500 Verified Legal PDFs   │                                         │ Supabase / SQLite Schema  │
   │  - Constitution (30)      │                                         │  - Document Registry      │
   │  - Federal Statutes (180) │                                         │  - Chat Sessions & Audit  │
   │  - Rules & Regs (60)      │                                         │  - User Feedback Metrics  │
   │  - 4 Provincial Codes(200)│                                         └───────────────────────────┘
   │  - Precedents (30)        │
   └───────────────────────────┘
```

---

## 📦 Verified 500-PDF Legal Corpus Breakdown

The initial corpus contains **exactly 500 unique, readable, and checksum-verified PDF legal documents** in `data/raw/`:

| Statutory Area | Mandatory Count | Verified Status | Provenance & Sources |
|---|---|---|---|
| **Constitution & Amendments** | 30 | 100% Verified | Constitution 1973 Consolidated + 1st through 26th Constitutional Amendments |
| **Core Federal Acts & Statutes** | 180 | 100% Verified | PPC 1860, CrPC 1898, CPC 1908, QSO 1984, Specific Relief, PECA, Companies Act 2017, ITO 2001, etc. |
| **Federal Rules & Regulations** | 60 | 100% Verified | Supreme Court Rules 1980, High Court Rules & Orders, Tax Rules, FIA & PECA Rules |
| **Punjab Provincial Laws** | 60 | 100% Verified | Punjab Land Revenue Act 1967, Tenancy Act 1887, Consumer Protection Act 2005, Local Govt 2022 |
| **Sindh Provincial Laws** | 50 | 100% Verified | Sindh Tenancy Act 1950, Sindh Local Govt Act 2013, Sindh Consumer Protection, SEPA 2014 |
| **Khyber Pakhtunkhwa Laws** | 50 | 100% Verified | KP Police Act 2017, KP Right to Information 2013, KP Local Government, Consumer Protection |
| **Balochistan Provincial Laws**| 40 | 100% Verified | Balochistan Land Revenue Act, Local Government 2010, Consumer Protection Act 2003 |
| **Supreme Court Precedents** | 20 | 100% Verified | Landmark Reported Judgments (PLD 1973 SC 49, PLD 1993 SC 473, PLD 2015 SC 401, PLD 2024 SC 1) |
| **High Court Precedents** | 10 | 100% Verified | Landmark Rulings from LHC, IHC, SHC, PHC, and BHC on writ jurisdiction and human rights |
| **Total** | **500** | **100% Delivered** | **All 500 PDFs verified with unique SHA-256 hashes in `corpus/manifest.csv`** |

---

## 🚀 Quick Start Guide

### Prerequisites
- **Node.js**: v18+ (tested on Node v24)
- **Python**: 3.11+ (tested on Python 3.14)
- **Git** (optional: Docker & Docker Compose)

---

### Step 1: Environment Setup
Copy the environment template:
```bash
# Windows PowerShell / CMD / Unix
cp .env.example .env
```
*(Optionally fill in your `GROQ_API_KEY` from https://console.groq.com/keys and Supabase keys. In development mode, smart fallbacks operate completely offline.)*

---

### Step 2: Install Dependencies

#### Frontend:
```bash
npm install
```

#### Backend:
```bash
py -3 -m pip install -r backend/requirements.txt
```
*(On Linux/macOS, use `python3 -m pip install -r backend/requirements.txt`)*

---

### Step 3: Verify Corpus Integrity
Run the automated validation suite to assert the mandatory 500-PDF rule:
```bash
py -3 backend/scripts/validate_corpus.py
```
Expected output:
```
SUCCESS: 500/500 PDFs verified!
  - Total Valid PDFs:       500
  - Total Manifest Entries: 500
  - Unique SHA-256 Hashes:  500
  - Checksum Integrity:     100% Passed
  - PyMuPDF Readability:    100% Passed
```

---

### Step 4: Run Ingestion Pipeline (One-Time Indexing)
Extract, chunk, embed, and index the 500 documents:
```bash
py -3 backend/scripts/ingest_corpus.py
```

---

### Step 5: Start the Full Stack

#### Start Backend API (FastAPI on Port 8000):
```bash
# Windows PowerShell / CMD
py -3 -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Start Frontend Dev Server (Vite on Port 5173):
```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🧪 Automated Testing & Evaluation

### Run Test Suite (Unit & Integration Tests)
```bash
py -3 -m pytest backend/tests -v
```
Verifies PDF extraction, legal hierarchy chunking, hybrid retrieval, Groq prompt formatting, Supabase JWT verification, and API routes (13/13 passing).

### Run 100-Query Retrieval Benchmark
```bash
py -3 eval/run_evaluation.py
```
Evaluates recall, MRR, citation accuracy, and prompt injection / out-of-domain refusal rates.

---

## 🐳 Docker Deployment (Optional)

Run the complete multi-service stack (Frontend, Backend, Qdrant, PostgreSQL) via Docker Compose:
```bash
docker-compose up --build -d
```

---

## 🛡️ Security & Ethical Guardrails
1. **Zero Secret Leaks:** Groq API keys and database credentials reside exclusively in the backend environment. Frontend bundles only receive Supabase public tokens.
2. **Strict Grounding:** The assistant synthesizes responses strictly from retrieved statutory provisions.
3. **Non-Advocate Disclaimer:** The system prominently emphasizes that it provides legal information and research assistance, not licensed advocate representation.
4. **Mandatory Refusal:** Non-legal queries, missing provisions, or adversarial prompt injections trigger explicit refusal responses.
