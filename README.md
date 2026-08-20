# AgentMed AI - Multi-Agent Medical Information Chatbot


AgentMed AI is a production-grade multi-agent medical information assistant built using **LangGraph, Model Context Protocol (MCP), FastAPI, and Streamlit**.


It accepts natural language queries about symptoms, medications, and general health, and routes them through a graph of specialized AI agents. Clinical responses are grounded with live PubMed research and a local medical knowledge base. Conversation history is persisted in PostgreSQL so the assistant remembers context across turns within a session.


> **Disclaimer:** This project is built for educational and informational purposes only. It does not diagnose, prescribe, or replace professional medical advice.


---


## Key Features


- **Multi-Agent Architecture:** Orchestrated via LangGraph. Six specialized agents — Router, Intake, Research, Clinical Reasoning, Safety, and Composer — each handle a single responsibility in the pipeline.


- **Intelligent Routing:** The Router agent classifies every message into one of five intents and short-circuits the graph for casual messages, so the database is never queried for greetings or off-topic input.


- **MCP-Grounded Research:** Live PubMed papers and a local Chroma knowledge base are retrieved via Model Context Protocol servers and injected into the final answer as cited sources.


- **Drug Interaction Safety:** A dedicated Safety agent independently checks for emergency red flags and calls the drug interaction MCP server when the user has listed active medications.


- **Persistent Conversation Memory:** LangGraph's `AsyncPostgresSaver` checkpoints the full message history to PostgreSQL after every turn, enabling true multi-turn memory across the entire session.


- **Real-Time Token Streaming:** The backend uses LangGraph's `astream_events` API to forward individual LLM tokens to the Streamlit frontend as Server-Sent Events, creating a smooth live typing experience.


- **Emergency Detection:** A deterministic rule-based scanner runs before any LLM call and immediately routes emergency phrases such as `"worst headache of my life"` to the Safety and Composer nodes, bypassing all research steps.


---


## Architecture and Component Flow


```text
User Message (Streamlit UI)
        |
        v
Input arrives at POST /chat/stream
        |
        v
Router Agent
  |
  +-- Deterministic red-flag scan (safety_rules.py)
  |
  +-- If emergency -> Safety
  |
  +-- If casual (greeting / off-topic) -> Safety
  |
  +-- Otherwise -> Intake
        |
        +-- (medical intent) -> Intake Agent
        |                       |
        |                       +-- Extracts symptoms and duration
        |                       |
        |                       v
        |                  Research Agent
        |                       |
        |                       +-- Calls pubmed_server MCP:
        |                       |   search_pubmed
        |                       |
        |                       +-- Calls vectorstore_server MCP:
        |                       |   search_knowledge_base
        |                       |
        |                       +-- Returns research_notes and sources
        |                       |
        |                       v
        |                  Clinical Reasoning Agent
        |                       |
        |                       +-- Synthesizes possible
        |                           non-diagnostic explanations
        |
        +-- (all paths converge here)
                                |
                                v
                         Safety Agent
                                |
                                +-- Re-scans input for red flags
                                |
Prerequisites
Python 3.11 or higher
uv package manager
PostgreSQL database
Render free tier
Supabase
Local PostgreSQL instance
Groq API key

Install uv:

pip install uv
Setup and Installation
1. Clone the Repository
git clone https://github.com/your-username/medical-chatbot.git
cd medical-chatbot
2. Create a Virtual Environment

Using uv:

uv venv

Windows:

.venv\Scripts\activate

macOS / Linux:

source .venv/bin/activate
3. Install Dependencies
uv sync
4. Configure Environment Variables

Create a .env file in the project root:

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
5. Initialize the Database

This creates the application tables for sessions and messages in PostgreSQL.

uv run python scripts/init_db.py
6. Ingest the Knowledge Base

Load patient education documents into the local Chroma vector store:

uv run python scripts/ingest_kb.py
Running the Application
1. Start the Backend

Run FastAPI:

uv run uvicorn backend.main:app --reload --port 8000

Open the API documentation:

http://localhost:8000/docs
2. Start the Frontend

Run this in a separate terminal.

Windows PowerShell:

$env:PYTHONPATH="."; uv run streamlit run frontend/streamlit_app.py

Linux / macOS:

PYTHONPATH=. uv run streamlit run frontend/streamlit_app.py

Open the application at:

http://localhost:8501
API Endpoints
POST /chat

Submits a message and returns the complete response as JSON.

Example payload:

{
  "message": "Is it safe to take ibuprofen?",
  "session_id": null,
  "current_medications": [
    "warfarin"
  ]
}
POST /chat/stream

Submits a message and returns a Server-Sent Events (SSE) stream containing:

Node progress labels
Individual LLM tokens
Final JSON payload

The payload is the same as /chat.

GET /history/{session_id}

Returns the complete message history for a given session.

GET /health

Returns:

{
  "status": "ok"
}
Project Structure
medical-chatbot/
|
+-- backend/
|   +-- main.py
|   +-- config.py
|
|   +-- api/
|   |   +-- chat.py
|   |   +-- history.py
|
|   +-- graph/
|   |   +-- graph.py
|   |   +-- state.py
|   |   +-- llm.py
|   |
|   |   +-- nodes/
|   |       +-- router.py
|   |       +-- intake.py
|   |       +-- research.py
|   |       +-- clinical_reasoning.py
|   |       +-- safety.py
|   |       +-- composer.py
|   |
|   +-- mcp_clients/
|   |   +-- client.py
|   |
|   +-- db/
|   |   +-- database.py
|   |
|   +-- models/
|   |
|   +-- utils/
|       +-- safety_rules.py
|
+-- mcp_servers/
|   +-- pubmed_server/
|   +-- drugdata_server/
|   +-- vectorstore_server/
|
+-- frontend/
|   +-- streamlit_app.py
|   |
|   +-- components/
|       +-- chat_ui.py
|       +-- sidebar.py
|       +-- emergency_banner.py
|
+-- scripts/
|   +-- init_db.py
|   +-- ingest_kb.py
|
+-- tests/
|
+-- pyproject.toml
+-- .env.example
Troubleshooting and Notes
1. MCP Library Version

The mcp library must be pinned below version 2.0.0.

FastMCP v2.0.0 moved the FastMCP class to a separate package, which breaks the MCP servers in this project.

Use:

mcp>=1.1.0,<2.0.0
2. PYTHONPATH on Windows

Streamlit must be launched from the project root with PYTHONPATH set to ".".

Otherwise, frontend imports may fail with:

ModuleNotFoundError

Use:

$env:PYTHONPATH="."; uv run streamlit run frontend/streamlit_app.py
3. PostgreSQL Event Loop on Windows

psycopg async mode is incompatible with the Windows ProactorEventLoop.

FastAPI uses Uvicorn, which automatically selects a compatible event loop.

If running async scripts directly on Windows, use:

import asyncio


asyncio.set_event_loop_policy(
    asyncio.WindowsSelectorEventLoopPolicy()
)

before making async calls.

4. Chroma Data

The chroma_db directory is gitignored.

After cloning the repository on a new machine, run:

uv run python scripts/ingest_kb.py

before starting the backend.

Otherwise, the vectorstore MCP server will have no documents to search.

5. Database Mode

PostgreSQL must be running and reachable through DATABASE_URL before starting the backend.

LangGraph uses AsyncPostgresSaver to persist graph state across Human-in-the-Loop threads.

Disclaimer

This application is intended for general educational and informational purposes only.

It is not a substitute for professional medical advice, diagnosis, or treatment.

Always consult a qualified healthcare provider for medical questions or concerns.