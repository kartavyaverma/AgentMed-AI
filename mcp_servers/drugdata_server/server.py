import json
import os

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("drugdata-server")

RXNAV_BASE = os.environ.get("RXNAV_BASE_URL", "https://rxnav.nlm.nih.gov/REST")
OPENFDA_BASE = os.environ.get("OPENFDA_BASE_URL", "https://api.fda.gov")

async def _rxcui_for_name(client: httpx.AsyncClient, drug_name: str) -> str | None:
    resp = await client.get(f"{RXNAV_BASE}/rxcui.json", params={"name": drug_name})
    resp.raise_for_status()
    ids = resp.json().get("idGroup", {}).get("rxnormId", [])
    return ids[0] if ids else None

@mcp.tool()
async def lookup_drug(drug_name: str) -> str:
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            f"{OPENFDA_BASE}/drug/label.json",
            params={"search": f'openfda.brand_name:"{drug_name}"', "limit": 1},
        )
        if resp.status_code != 200:
            return json.dumps({"name": drug_name, "found": False, "warnings": [], "purpose": None})

        results = resp.json().get("results", [])
        if not results:
            return json.dumps({"name": drug_name, "found": False, "warnings": [], "purpose": None})

        doc = results[0]
        return json.dumps(
            {
                "name": drug_name,
                "found": True,
                "warnings": doc.get("boxed_warning", doc.get("warnings", [])),
                "purpose": doc.get("purpose", []),
                "contraindications": doc.get("contraindications", []),
            }
        )

@mcp.tool()
async def check_interactions(drug_names: list[str]) -> str:
    async with httpx.AsyncClient(timeout=15) as client:
        rxcuis = []
        for name in drug_names:
            rxcui = await _rxcui_for_name(client, name)
            if rxcui:
                rxcuis.append(rxcui)

        if len(rxcuis) < 2:
            return json.dumps({"checked": drug_names, "interactions": [], "note": "fewer than 2 drugs resolved"})

        resp = await client.get(
            f"{RXNAV_BASE}/interaction/list.json",
            params={"rxcuis": "+".join(rxcuis)},
        )
        resp.raise_for_status()
        data = resp.json()

    interactions = []
    for group in data.get("fullInteractionTypeGroup", []):
        for itype in group.get("fullInteractionType", []):
            for pair in itype.get("interactionPair", []):
                interactions.append(
                    {
                        "description": pair.get("description"),
                        "severity": pair.get("severity", "unknown"),
                    }
                )

    return json.dumps({"checked": drug_names, "interactions": interactions})

if __name__ == "__main__":
    mcp.run(transport="stdio")
