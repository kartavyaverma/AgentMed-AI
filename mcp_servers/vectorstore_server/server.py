import json
from pathlib import Path

import chromadb
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("vectorstore-server")

CHROMA_DIR = Path(__file__).parent / "chroma_data"
CHROMA_DIR.mkdir(exist_ok=True)

_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
_collection = _client.get_or_create_collection(name="medical_kb")

@mcp.tool()
async def search_knowledge_base(query: str, top_k: int = 4) -> str:
    if _collection.count() == 0:
        return json.dumps([])

    results = _collection.query(query_texts=[query], n_results=top_k)

    docs = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    output = []
    for doc, meta, dist in zip(docs, metadatas, distances):
        output.append(
            {
                "text": doc,
                "source": (meta or {}).get("source", "internal_kb"),
                "score": dist,
            }
        )
    return json.dumps(output)

if __name__ == "__main__":
    mcp.run(transport="stdio")
