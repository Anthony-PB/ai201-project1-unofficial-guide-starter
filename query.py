"""
Milestone 5: Grounded Generation
Unofficial Guide to CS Courses at Cornell

ask(question) -> {"answer": str, "sources": list[str]}
  - Retrieves top-k chunks from ChromaDB
  - Builds a strict grounding prompt
  - Calls Groq llama-3.3-70b-versatile
  - Returns answer + programmatically extracted source list
"""

import os
from dotenv import load_dotenv
from groq import Groq

from embed import retrieve

load_dotenv()

GROQ_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """\
You are a helpful assistant for Cornell CS students. Your ONLY job is to answer \
questions using the document excerpts provided in the user message.

STRICT RULES — follow these without exception:
1. Answer ONLY from the provided document excerpts. Do NOT use any outside knowledge,
   training data, or general assumptions about Cornell or CS courses.
2. If the excerpts do not contain enough information to answer the question, respond
   with exactly: "I don't have enough information on that."
3. Do not speculate, infer, or fill gaps with general knowledge. If a detail is not
   stated in the excerpts, do not include it.
4. Keep your answer focused and grounded strictly in what the excerpts explicitly state.\
"""


def _build_context(chunks: list[dict]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(f"[{i}] (source: {chunk['source']})\n{chunk['text']}")
    return "\n\n".join(parts)


def ask(question: str) -> dict:
    """
    End-to-end RAG pipeline.

    Args:
        question: natural-language question from the user

    Returns:
        {"answer": str, "sources": list[str]}
        Sources are deduplicated filenames from retrieved chunk metadata —
        programmatically guaranteed, not left to the LLM.
    """
    chunks = retrieve(question)

    context = _build_context(chunks)

    user_message = (
        f"Document excerpts:\n{context}\n\nQuestion: {question}"
    )

    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,
        max_tokens=512,
    )

    answer = response.choices[0].message.content.strip()

    # Programmatic source attribution — ordered by first appearance, deduplicated
    seen: set[str] = set()
    sources: list[str] = []
    for chunk in chunks:
        src = chunk["source"]
        if src not in seen:
            seen.add(src)
            sources.append(src)

    return {"answer": answer, "sources": sources}
