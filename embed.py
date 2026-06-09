"""
Milestone 4: Embedding and Retrieval
Unofficial Guide to CS Courses at Cornell

embed_chunks() — embeds all chunks with all-MiniLM-L6-v2, stores in ChromaDB
retrieve()     — takes a query string, returns top-k chunks with source + distance
"""

import chromadb
from sentence_transformers import SentenceTransformer

from pipeline import load_and_chunk

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "cornell_cs_guide"
TOP_K = 5

# ---------------------------------------------------------------------------
# Embedding
# ---------------------------------------------------------------------------

def embed_chunks(chunks: list[dict]) -> chromadb.Collection:
    """
    Embed all chunks with all-MiniLM-L6-v2 and store in a local ChromaDB collection.
    Rebuilds the collection from scratch on each call to avoid duplicate IDs.

    Args:
        chunks: list of {"text": str, "source": str} dicts from load_and_chunk()

    Returns:
        The populated ChromaDB collection.
    """
    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)

    print(f"Embedding {len(chunks)} chunks...")
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_list=True)

    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Always rebuild so re-runs don't produce duplicate IDs
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(
        COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    # Build parallel lists for ChromaDB bulk add
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    metadatas = [
        {"source": c["source"], "chunk_index": i}
        for i, c in enumerate(chunks)
    ]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )

    print(f"Stored {collection.count()} chunks in ChromaDB at {CHROMA_PATH!r}")
    return collection


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------

def retrieve(query: str, k: int = TOP_K) -> list[dict]:
    """
    Embed a query and return the top-k most similar chunks.

    Args:
        query: natural-language question string
        k:     number of results to return (default 4)

    Returns:
        List of dicts, each with keys:
          "text"        — chunk content
          "source"      — source document name
          "chunk_index" — position in that document
          "distance"    — cosine distance (lower = more similar)
    """
    model = SentenceTransformer(EMBEDDING_MODEL)
    query_embedding = model.encode(query, convert_to_list=True)

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_collection(COLLECTION_NAME)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for text, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({
            "text": text,
            "source": meta["source"],
            "chunk_index": meta["chunk_index"],
            "distance": round(dist, 4),
        })
    return chunks


# ---------------------------------------------------------------------------
# Test retrieval with 3 eval queries
# ---------------------------------------------------------------------------

TEST_QUERIES = [
    "What do students say about the difficulty of problem sets in CS3110?",
    "What courses do students recommend as prerequisites before taking CS4780?",
    "What do students say about the workload and project structure in CS4780?",
]


def test_retrieval():
    for query in TEST_QUERIES:
        print("\n" + "=" * 60)
        print(f"QUERY: {query}")
        print("=" * 60)
        results = retrieve(query)
        for i, r in enumerate(results, 1):
            print(f"\n  [{i}] source={r['source']}  distance={r['distance']}")
            print(f"  {'-' * 48}")
            print(f"  {r['text']}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Build pipeline and embed
    chunks = load_and_chunk()
    print()
    embed_chunks(chunks)

    # Test retrieval
    # print()
    # print("=" * 60)
    # print("Retrieval test — 3 eval queries")
    # print("=" * 60)
    # test_retrieval()
