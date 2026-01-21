# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Swig GM Dashboard - An AI-powered General Manager co-pilot for Swig restaurant franchise operations. Full-stack application with React frontend and Python FastAPI backend, using DuckDB for operational analytics and OpenAI for conversational AI.

## Quick Start

From `swig-gm-dashboard/` directory:
```bash
./start.sh   # Starts both frontend and backend, creates venv and installs deps if needed
```

Or manually:
```bash
# Backend (from swig-gm-dashboard/backend/)
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (from swig-gm-dashboard/frontend/)
npm install
npm run dev
```

## Development Commands

**Frontend** (`swig-gm-dashboard/frontend/`):
- `npm run dev` - Start Vite dev server (http://localhost:5173)
- `npm run build` - TypeScript check + production build
- `npm run lint` - Run ESLint

**Backend** (`swig-gm-dashboard/backend/`):
- `uvicorn app.main:app --reload --port 8000` - Development server
- API docs available at http://localhost:8000/docs

## Architecture

```
Frontend (React/TypeScript/Vite)
    ↓ /api/* (proxied via Vite in dev)
Backend (FastAPI)
    ↓
GM Agent (OpenAI function calling)
    ↓
DuckDB (read-only operational data)
```

**Frontend structure** (`frontend/src/`):
- `components/` - React components (KPICards, ThroughputChart, ChatPanel, ComplianceCard, WhoIsWorking)
- `services/api.ts` - API client using React Query

**Backend structure** (`backend/app/`):
- `routers/` - API endpoints (dashboard, workforce, transactions, chat)
- `agent/gm_agent.py` - OpenAI agent with tools for querying operations data
- `database.py` - Singleton DuckDB connection manager
- `config.py` - Pydantic settings from environment

**API Routes**:
- `/api/dashboard/*` - KPIs, hourly throughput, alerts
- `/api/workforce/*` - Employee roster, compliance violations
- `/api/transactions/*` - Sales transaction queries
- `/api/chat` - Conversational AI endpoint

## Environment Variables

Backend requires `backend/.env` with:
- `OPENAI_API_KEY` - For GPT-based GM agent (or falls back to AWS Bedrock)
- `DUCKDB_PATH` - Optional, defaults to `../swig_operations.duckdb`

## Domain Context

- **Swig**: Quick-service "dirty soda" restaurant chain
- **Dirty Sodas**: Customizable soda + flavor/cream modifiers
- **Linebusting**: Upstream ordering via tablets in drive-thru queue
- **Core metrics**: Revenue, throughput (cars/hr), labor %, compliance violations
- **Synthetic data**: 3 weeks (Jan 6-26, 2025), Store IDs: 1001, 1002, 1003

## Data Generator

`swig_data_generator/` contains standalone Python project for generating synthetic operational data into DuckDB.
