# 🌾 Project Samarth - Intelligent Agricultural Q&A System

> A RAG-based AI system for querying Indian agricultural data with 2025 government policy integration

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.2-blue.svg)](https://reactjs.org)
[![LangChain](https://img.shields.io/badge/LangChain-0.1.20-orange.svg)](https://langchain.com)
[![FAISS](https://img.shields.io/badge/FAISS-1.12.0-red.svg)](https://github.com/facebookresearch/faiss)

## 🎯 Overview

Project Samarth is an intelligent Q&A system that provides accurate, cited answers about Indian agriculture by integrating:

- **Government Data**: Live data from data.gov.in covering agriculture production, rainfall, and climate
- **2025 Policies**: Latest government schemes including PM Dhan-Dhaanya Krishi Yojana (₹24,000 crore)
- **Real-time Context**: e-NAM platform data (1.79 crore registered farmers)
- **Advanced AI**: RAG architecture with FAISS vector search and LangChain orchestration

## 📊 Key Statistics (2025 Edition)

- 🌾 **Food grain production**: 353.96 million tonnes (2024-25)
- 💰 **Agriculture budget**: ₹1,37,756.55 crore (2025-26)
- 👥 **e-NAM farmers**: 1.79 crore registered
- 🌧️ **Climate data**: 1901-2024 IMD rainfall records
- 📍 **Coverage**: All Indian states and districts

## 🏠 Architecture

```
┌────────────────────┐
│    React Frontend     │
├────────────────────┤
│    FastAPI Backend    │
├────────────────────┤
│   LangChain + RAG    │
├────────────────────┤
│  FAISS Vector Store  │
├────────────────────┤
│ Data Harmonization  │
├────────────────────┤
│  Government Data     │
│  • data.gov.in       │
│  • IMD Rainfall      │
│  • e-NAM Platform    │
│  • Policy Updates    │
└────────────────────┘
```

## 🚀 Quick Start (Windows friendly)

### Prerequisites
- Python 3.11+ (3.12 supported)
- Node.js 18+
- Git

We use FAISS-only on Windows (no Chroma). No C++ build tools needed.

### 1. Clone & Setup
```bash
git clone https://github.com/rkbharti/project-samarth.git
cd project-samarth

# Create virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
# source venv/bin/activate

# Install dependencies with constraints
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt -c constraints.txt --upgrade
```

### 2. Data Setup (First Run)
```bash
python scripts/setup_data.py
```
- This builds knowledge chunks and attempts FAISS vectorstore.
- If sentence-transformers is missing, the script completes and you can still run the API.

### 3. Start Backend (project root)
```bash
uvicorn backend.main:app --reload --port 8000
```

### 4. Start Frontend
```bash
cd frontend
npm install
npm start
```

### 5. Access Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🔁 Embedding Options
- Default: HuggingFace embeddings (local)
- Optional: OpenAI embeddings. Set in .env:
```
USE_OPENAI_EMBEDDINGS=true
OPENAI_API_KEY=sk-...
```
Then restart backend.

## 🧰 Troubleshooting
- "Microsoft Visual C++… is required": Not needed anymore. We removed Chroma.
- "Could not import sentence_transformers":
  - Install with constraints: `pip install -r requirements.txt -c constraints.txt`
  - Or switch to OpenAI embeddings via .env as above
- Import path errors: All imports are absolute from `backend.*`, run uvicorn from project root as shown.

## 📚 Data Sources
- data.gov.in (agriculture statistics)
- IMD (rainfall and climate)
- e-NAM (market data)
- APEDA, Ministry of Agriculture (policies & budgets)

## 📝 License
MIT License - see [LICENSE](LICENSE)
