import json

from langchain_core.messages import SystemMessage, HumanMessage

from backend.graph.llm import get_llm
from backend.graph.state import MedicalChatState, SourceDict
from backend.mcp_clients.client import call_mcp_tool

SYNTHESIS_SYSTEM_PROMPT = """You are a medical research assistant. Summarize the \
provided evidence snippets into 3-5 concise, neutral bullet points relevant to \
the user's question. Do NOT diagnose. Do NOT recommend treatment. Stick to what \
the evidence says. If evidence is thin, say so plainly."""

async def research_node(state: MedicalChatState) -> dict:
    if state.get("is_emergency"):
        return {"research_notes": "", "sources": []}

    query = state["user_input"]
    symptoms = state.get("extracted_symptoms", [])
    search_query = query if not symptoms else f"{query} ({', '.join(symptoms)})"

    pubmed_raw = await call_mcp_tool("pubmed", "search_pubmed", {"query": search_query, "max_results": 4})
    kb_raw = await call_mcp_tool("vectorstore", "search_knowledge_base", {"query": search_query, "top_k": 4})

    pubmed_results = json.loads(pubmed_raw) if pubmed_raw else []
    kb_results = json.loads(kb_raw) if kb_raw else []

    sources: list[SourceDict] = []
    evidence_snippets = []

    for r in pubmed_results:
        sources.append({"title": r.get("title", "Untitled"), "url": r.get("url"), "source_type": "pubmed"})
        evidence_snippets.append(f"[PubMed] {r.get('title')}: {r.get('summary', '')}")

    for r in kb_results:
        sources.append({"title": r.get("source", "Internal KB"), "url": None, "source_type": "internal_kb"})
        evidence_snippets.append(f"[KB] {r.get('text', '')}")

    if not evidence_snippets:
        return {"research_notes": "No specific evidence retrieved for this query.", "sources": []}

    llm = get_llm("research", temperature=0.2)
    response = await llm.ainvoke(
        [
            SystemMessage(content=SYNTHESIS_SYSTEM_PROMPT),
            HumanMessage(content=f"Question: {query}\n\nEvidence:\n" + "\n".join(evidence_snippets)),
        ]
    )

    return {"research_notes": response.content, "sources": sources}
