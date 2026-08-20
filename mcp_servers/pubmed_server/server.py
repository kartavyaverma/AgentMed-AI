import json
import os

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("pubmed-server")

NCBI_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
API_KEY = os.environ.get("PUBMED_API_KEY")                               

@mcp.tool()
async def search_pubmed(query: str, max_results: int = 5) -> str:
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": max_results,
        "sort": "relevance",
    }
    if API_KEY:
        params["api_key"] = API_KEY

    async with httpx.AsyncClient(timeout=15) as client:
        search_resp = await client.get(f"{NCBI_BASE}/esearch.fcgi", params=params)
        search_resp.raise_for_status()
        id_list = search_resp.json().get("esearchresult", {}).get("idlist", [])

        if not id_list:
            return json.dumps([])

        summary_params = {
            "db": "pubmed",
            "id": ",".join(id_list),
            "retmode": "json",
        }
        if API_KEY:
            summary_params["api_key"] = API_KEY

        summary_resp = await client.get(f"{NCBI_BASE}/esummary.fcgi", params=summary_params)
        summary_resp.raise_for_status()
        summary_data = summary_resp.json().get("result", {})

    results = []
    for pmid in id_list:
        doc = summary_data.get(pmid, {})
        if not doc:
            continue
        results.append(
            {
                "title": doc.get("title", "Untitled"),
                "pmid": pmid,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "summary": doc.get("elocationid", "") or doc.get("source", ""),
                "pub_date": doc.get("pubdate", ""),
            }
        )
    return json.dumps(results)

if __name__ == "__main__":
    mcp.run(transport="stdio")
