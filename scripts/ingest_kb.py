from pathlib import Path

import chromadb

CHROMA_DIR = Path(__file__).parent.parent / "mcp_servers" / "vectorstore_server" / "chroma_data"
CHROMA_DIR.mkdir(exist_ok=True, parents=True)

SAMPLE_DOCS = [
    {
        "id": "kb-001",
        "text": (
            "Common cold symptoms (runny nose, sore throat, mild cough, low-grade "
            "fever) typically resolve within 7-10 days with rest and fluids. "
            "Persistent fever above 103F/39.4C, symptoms lasting beyond 10 days, "
            "or worsening after initial improvement warrant medical evaluation."
        ),
        "source": "General Patient Education - Upper Respiratory Infections",
    },
    {
        "id": "kb-002",
        "text": (
            "Tension headaches are commonly associated with stress, poor posture, "
            "dehydration, or lack of sleep. Migraine is distinguished by throbbing "
            "pain often on one side, sensitivity to light/sound, and sometimes "
            "visual aura. Sudden 'worst headache of life' onset requires urgent care."
        ),
        "source": "General Patient Education - Headache Disorders",
    },
    {
        "id": "kb-003",
        "text": (
            "NSAIDs (e.g. ibuprofen) and acetaminophen/paracetamol are commonly "
            "used for pain and fever, but should not be combined with certain "
            "blood thinners or in patients with specific kidney/liver conditions "
            "without medical guidance. Always check for interactions."
        ),
        "source": "General Patient Education - OTC Pain Relievers",
    },
]

def main():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(name="medical_kb")

    collection.upsert(
        ids=[d["id"] for d in SAMPLE_DOCS],
        documents=[d["text"] for d in SAMPLE_DOCS],
        metadatas=[{"source": d["source"]} for d in SAMPLE_DOCS],
    )
    print(f"Ingested {len(SAMPLE_DOCS)} documents into 'medical_kb' collection.")

if __name__ == "__main__":
    main()
