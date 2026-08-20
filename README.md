# AgentMed AI - Multi-Agent Medical Information Chatbot

AgentMed AI is a production-grade multi-agent medical information assistant built using LangGraph, Model Context Protocol (MCP), FastAPI, and Streamlit. It accepts natural language queries about symptoms, medications, and general health, and routes them through a graph of specialized AI agents. Clinical responses are grounded with live PubMed research and a local medical knowledge base. Conversation history is persisted in PostgreSQL so the assistant remembers context across turns within a session.

This project is built for educational and informational purposes only. It does not diagnose, prescribe, or replace professional medical advice.

## Key Features

- Multi-Agent Architecture: Orchestrated via LangGraph. Six specialized agents (Router, Intake, Research, Clinical Reasoning, Safety, Composer) each handle a single responsibility in the pipeline.
- Intelligent Routing: The Router agent classifies every message into one of five intents and short-circuits the graph for casual messages, so the database is never queried for greetings or off-topic input.
- MCP-Grounded Research: Live PubMed papers and a local Chroma knowledge base are retrieved via Model Context Protocol servers and injected into the final answer as cited sources.
- Drug Interaction Safety: A dedicated Safety agent independently checks for emergency red flags and calls the drug interaction MCP server when the user has listed active medications.
- Persistent Conversation Memory: LangGraph's AsyncPostgresSaver checkpoints the full message history to PostgreSQL after every turn, enabling true multi-turn memory across the entire session.
- Real-Time Token Streaming: The backend uses LangGraph's astream_events API to forward individual LLM tokens to the Streamlit frontend as Server-Sent Events, creating a smooth live typing experience.
- Emergency Detection: A deterministic rule-based scanner runs before any LLM call and immediately routes emergency phrases (e.g. "worst headache of my life") to the Safety and Composer nodes, bypassing all research steps.

## Architecture and Component Flow

User Message (Streamlit UI)
       |
       v
  Input arrives at POST /chat/stream (FastAPI, SSE)
       |
       v
  Router Agent
    - Deterministic red-flag scan (safety_rules.py)
    - If emergency: route directly to Safety
    - If casual (greeting / off-topic): route directly to Safety (skip research)
    - Otherwise: route to Intake
       |
       +-- (medical intent) --> Intake Agent
       |                          - Extracts symptoms and duration from free text
       |                               |
       |                               v
       |                        Research Agent
       |                          - Calls pubmed_server MCP: search_pubmed
       |                          - Calls vectorstore_server MCP: search_knowledge_base
       |                          - Returns research_notes and sources
       |                               |
       |                               v
       |                        Clinical Reasoning Agent
       |                          - Synthesizes possible (non-diagnostic) explanations
       |
       +-- (all paths converge here) --> Safety Agent
       |                          - Re-scans input for red flags independently
       |                          - Calls drugdata_server MCP: check_interactions
       |                            (only if user has listed medications)
       |
       v
  Composer Agent
    - Combines research notes, possible explanations, drug warnings
    - Loads full PostgreSQL-persisted conversation history
    - Streams final answer token-by-token back to client
    - Appends HumanMessage + AIMessage to LangGraph checkpoint
       |
       v
  Streamlit UI
    - Renders node progress labels in real time
    - Renders streamed tokens word-by-word
    - Displays cited sources in an expandable section
    - Saves session_id for next turn

## Prerequisites

- Python 3.11 or higher
- uv package manager (install with: pip install uv)
- PostgreSQL database (Render free tier, Supabase, or a local instance)
- A Groq API key (free at console.groq.com)

## Setup and Installation

### 1. Clone the Repository

`
git clone https://github.com/your-username/medical-chatbot.git
cd medical-chatbot
`

### 2. Create a Virtual Environment

Using uv (recommended):
`
uv venv
.venv\Scripts\activate       # Windows
source .venv/bin/activate    # macOS / Linux
`

### 3. Install Dependencies

`
uv sync
`

### 4. Configure Environment Variables

Create a .env file in the project root:
`
# LLM via Groq
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL_LARGE=openai/gpt-oss-120b
GROQ_MODEL_SMALL=openai/gpt-oss-20b

# PostgreSQL (application data + LangGraph checkpointing)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
APP_ENV=development
SECRET_KEY=change_me_to_a_random_string

# External APIs (used by MCP servers)
PUBMED_API_KEY=optional_ncbi_api_key
RXNAV_BASE_URL=https://rxnav.nlm.nih.gov/REST
OPENFDA_BASE_URL=https://api.fda.gov

# Frontend
BACKEND_BASE_URL=http://localhost:8000
`

### 5. Initialize the Database

Creates the application tables (sessions, messages) in your PostgreSQL database.
`
uv run python scripts/init_db.py
`

### 6. Ingest the Knowledge Base

Loads patient education documents into the local Chroma vector store.
`
uv run python scripts/ingest_kb.py
`

## Running the Application

### 1. Start the Backend (FastAPI)

`
uv run uvicorn backend.main:app --reload --port 8000
`

Open http://localhost:8000/docs for the interactive API documentation.

### 2. Start the Frontend (Streamlit)

Run this in a separate terminal. The PYTHONPATH must be set to the project root so the frontend package is importable.

On Windows (PowerShell):
`
="."; uv run streamlit run frontend/streamlit_app.py
`

On Linux or macOS:
`
PYTHONPATH=. uv run streamlit run frontend/streamlit_app.py
`

Open http://localhost:8501 in your browser.

## API Endpoints

- POST /chat: Submits a message and returns the full response as a JSON object.
  Payload: { "message": "Is it safe to take ibuprofen?", "session_id": null, "current_medications": ["warfarin"] }

- POST /chat/stream: Submits a message and returns a Server-Sent Events stream with node progress labels, individual LLM tokens, and a final JSON payload.
  Payload: same as /chat

- GET /history/{session_id}: Returns the full message history for a given session.

- GET /health: Returns { "status": "ok" } for health checks.

## Project Structure

`
medical-chatbot/
├── backend/
│   ├── main.py                   # FastAPI entrypoint
│   ├── config.py                 # Centralized settings via pydantic-settings
│   ├── api/
│   │   ├── chat.py               # POST /chat and POST /chat/stream (SSE)
│   │   └── history.py            # GET /history/{session_id}
│   ├── graph/
│   │   ├── graph.py              # LangGraph builder and checkpointer setup
│   │   ├── state.py              # MedicalChatState TypedDict
│   │   ├── llm.py                # Groq LLM factory
│   │   └── nodes/
│   │       ├── router.py
│   │       ├── intake.py
│   │       ├── research.py
│   │       ├── clinical_reasoning.py
│   │       ├── safety.py
│   │       └── composer.py
│   ├── mcp_clients/
│   │   └── client.py             # Generic MCP subprocess client
│   ├── db/
│   │   └── database.py           # SQLAlchemy engine and session
│   ├── models/                   # ORM models for sessions and messages
│   └── utils/
│       └── safety_rules.py       # Deterministic red-flag detection
├── mcp_servers/
│   ├── pubmed_server/            # MCP tool: search_pubmed
│   ├── drugdata_server/          # MCP tools: lookup_drug, check_interactions
│   └── vectorstore_server/       # MCP tool: search_knowledge_base (Chroma)
├── frontend/
│   ├── streamlit_app.py          # Streamlit entrypoint
│   └── components/
│       ├── chat_ui.py            # Message rendering and SSE stream parser
│       ├── sidebar.py            # Patient context input panel
│       └── emergency_banner.py   # Emergency alert overlay
├── scripts/
│   ├── init_db.py                # Creates database tables
│   └── ingest_kb.py              # Ingests documents into Chroma vector store
├── tests/
├── pyproject.toml                # uv-managed project dependencies
└── .env.example                  # Environment variable template
`

## Troubleshooting and Notes

- MCP Library Version: The mcp library must be pinned to a version below 2.0.0. In FastMCP v2.0.0, the FastMCP class was moved to a separate package, which breaks all MCP servers in this project. All four pyproject.toml files already include the constraint `mcp>=1.1.0,<2.0.0`.
- PYTHONPATH on Windows: Streamlit must be launched from the project root with PYTHONPATH set to "." otherwise the frontend package imports will fail with ModuleNotFoundError.
- PostgreSQL Event Loop on Windows: psycopg async mode is incompatible with the Windows ProactorEventLoop. The FastAPI server uses uvicorn which automatically selects a compatible event loop. If running async scripts directly on Windows, set asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) before any async calls.
- Chroma Data: The chroma_db directory is gitignored. After cloning the repository on a new machine, you must run `uv run python scripts/ingest_kb.py` before starting the backend, otherwise the vectorstore MCP server will have no documents to search.
- Database Mode: PostgreSQL must be running and reachable at the DATABASE_URL before starting the backend. LangGraph uses AsyncPostgresSaver to persist graph state across Human-in-the-Loop threads.

## Disclaimer

This application is for general educational and informational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider for any medical questions or concerns.
