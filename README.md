# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

Unofficial guide to CS courses at Cornell. This knowledge is valuable because it provides insight into CS courses from the perspective of students who have actually taken them. Official course rosters only give prerequisites and dry descriptions — they don't tell you the actual project workloads, which professors give the best feedback, or how difficult the weekly assignments are.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Unofficial Cornell CS Wiki — CS3110 | Text file | `data/about_CS3110.txt` |
| 2 | r/Cornell — CS2800 and CS3110 difficulty | Reddit thread | `data/CS2800_CS3110.txt` |
| 3 | r/Cornell — CS4780 probability prereq | Reddit thread | `data/prob_prereq.txt` |
| 4 | r/Cornell — best CS electives | Reddit thread | `data/best_electives.txt` |
| 5 | r/Cornell — honest CS questions (industry focus) | Reddit thread | `data/honest.txt` |
| 6 | Unofficial Cornell CS Wiki — FAQ | HTML (scraped) | https://cornellcswiki.gitlab.io/faq.html |
| 7 | CUReviews — CS4780 student reviews | Text file | `data/reviews_CS4780.txt` |
| 8 | CS major course sequence overview | Text file | `data/cs.txt` |
| 9 | Cornell Academic Catalog — CS BS requirements | Text file | `data/catalog.txt` |
| 10 | Cornell Engineering Handbook — CS core checklist | Text file | `data/engineering_handbook.txt` |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 450 characters

**Overlap:** 75 characters

**Why these choices fit your documents:** The corpus mixes short Reddit opinions (1–3 sentences) with longer FAQ and handbook text. 450 characters captures a complete review thought without merging unrelated opinions. The 75-character overlap ensures facts that straddle a boundary (e.g., a course name in one sentence, the opinion in the next) appear in at least one complete chunk. Any preprocessing strips HTML tags, bare URLs, CUReviews boilerplate lines (standalone ratings, date lines, UI chrome), and normalizes whitespace before chunking.

**Final chunk count:** 190
---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`. Chosen for its strong balance of performance and speed on general English text, which fits the Reddit and FAQ documents in this corpus.

**Production tradeoff reflection:** A more powerful model like a fine-tuned BERT variant or a larger OpenAI embedding model could improve accuracy on domain-specific language (e.g., course names, CS jargon) but would increase latency and cost. In a real deployment, user experience would weigh heavily toward a faster model. A larger context-length embedding model would also allow retrieving more chunks (e.g., top-10) for richer context, but risks including more irrelevant passages that could confuse generation.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:** The system prompt gives the model four explicit rules: (1) answer ONLY from the provided document excerpts — no outside knowledge or training data; (2) if the excerpts don't contain enough information, respond with exactly "I don't have enough information on that."; (3) do not speculate, infer, or fill gaps with general knowledge; (4) keep the answer strictly grounded in what the excerpts explicitly state. The instruction is framed as `STRICT RULES <-> follow these without exception` rather than a suggestion.

**How source attribution is surfaced in the response:** Source names are extracted programmatically from ChromaDB chunk metadata after retrieval — they are never generated by the LLM. The `ask()` function collects the `"source"` field from each retrieved chunk, deduplicates them in order of appearance, and returns them as a separate `"sources"` list. The Gradio interface displays this list in its own output box, guaranteeing attribution even if the model's answer doesn't mention sources.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about the workload in CS3110? | Students describe CS3110 as having challenging weekly OCaml problem sets; some students call it one of the hardest required CS courses. Heavy workload. | Students describe the workload in CS3110 as "Heavy but doable" with six assignments, one prelim, a final, and a large group project. Workload may have decreased a bit from this level. | Relevant | Accurate |
| 2 | What are the most commonly recommended CS electives for students interested in ML/AI? | CS4780, CS4782, and CS4787 are frequently mentioned. | The CS electives relevant to ML/AI are CS 3700: Foundations of AI Reasoning and Decision-Making, CS 3780: Introduction to Machine Learning, and CS 4780: Machine Learning. | Relevant | Accurate |
| 3 | What courses do students recommend as prerequisites before taking CS4780? | Students recommend taking a solid probability course (like MATH 4710 or ECE 3100) before CS4780. | I don't have enough information on that. | Partially Relevant | Accurate |
| 4 | What are the minimum GPA requirements to affiliate with the CS major at Cornell Engineering? | Students must maintain a certain GPA in core courses; C is the absolute minimum generally but grouped courses require a higher average GPA. | The minimum GPA requirements to affiliate with the CS major at Cornell Engineering is an average of 2.5 or better in ECE 2400/ENGRD 2140 and CS 2800/CS 2802 and CS 3110. | Relevant | Accurate |
| 5 | What do students say about the workload and project structure in CS4780? | Students note heavy theoretical content and programming projects; CUReviews comments reflect mixed opinions on difficulty. | According to the excerpts, students say that CS4780 has a significant workload, with problem sets and assignments being less frequent than once a week, and only 1 prelim. One student mentions that there was a lot of work, including coding assignments and normal homeworks every week, but notes that it's doable if you attend discussion/lecture or watch asynchronously. Another student recommends taking the class for CS majors. Additionally, a student notes that the class "sucks up more time than I thought it would". | Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**
What courses do students recommend as prerequisites before taking CS4780?
**What the system returned:**
I don't have enough information on that.
**Root cause (tied to a specific pipeline stage):**
The answer exists in `prob_prereq.txt`, the document lists ECE3100, MATH4710, ECON3130, ENGRD2700, and BTRY3080 as options, with comments recommending ECE3100 and ECON3130. The failure is at the **retrieval stage**: the query uses the framing "what do students recommend as prerequisites," but `prob_prereq.txt` frames the discussion as "what counts as the probability theory prerequisite" and "which is easiest." This semantic mismatch means the embedding for the query aligns more strongly with chunks that discuss generally about prerequisites in other contexts, and the most information-dense chunk from `prob_prereq.txt` (which contains all the course names) likely ranked below or at the edge of the top-k threshold. The generation stage then correctly enforced the grounding rule —> it had insufficient context and refused to answer rather than guessing.

**What you would change to fix it:**
Two options: (1) rephrase the query to match the document's framing, e.g., "Which probability course should I take before CS4780?" — this aligns more closely with how `prob_prereq.txt` is written and would likely surface the right chunks. (2) Increase `TOP_K` in `embed.py` from 5 to 7 or 8, giving retrieval more room to capture the relevant chunk even when it ranks lower. Option 1 is the lower-cost fix; option 2 helps generally but risks including more off-topic chunks in the LLM context. I can also just add more explicit mentions of "CS4780 prerequisites" in the `prob_prereq.txt` document to improve embedding alignment without changing the query or retrieval parameters or add a new document that directly addresses the question of CS4780 prerequisites to ensure it surfaces more strongly for that query.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**
The spec forced me to concretely define my chunking strategy and grounding mechanism before writing code, which made implementation much smoother. I had a clear plan on how to utilize the AI model to help me implement specific functions, and I knew exactly what to test for in my evaluation.
**One way your implementation diverged from the spec, and why:**
Well I already changed the spec to reflect my divergence but the main divergence was the removal of the reddit threads as a url source and instead using text files. I found that scraping the reddit threads was simply not allowed. I had to manually copy-paste the reddit threads into text files, which was a bit of a pain but ultimately allowed me to keep the same content in my corpus without violating any scraping rules.
---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
I gave Claude my Chunking Strategy section from planning.md and asked it to implement load_and_chunk().
- *What it produced:*
Claude returned a function that loads documents from a list of file paths, preprocesses the text by stripping HTML tags and normalizing whitespace, and then chunks the text into fixed-size character chunks with overlap. The function also returns metadata for each chunk, including the source document name.
- *What I changed or overrode:*
The generated function used a hardcoded file list, which I changed to DATA_DIR.glob("*.txt") for auto-discovery; the boilerplate cleaning regex was also expanded after testing revealed CUReviews-specific noise (rating numbers, date lines, UI chrome) in the chunks.

**Instance 2**

- *What I gave the AI:*
I gave Claude my Architecture diagram and Retrieval Approach section and ask it to implement embed_chunks(). I also provided it with the expected input and output formats for the function. (Roughly: input is a list of chunk dictionaries with "text" and "metadata", output is a list of embedding vectors and corresponding metadata.)
- *What it produced:*
Claude returned a function that takes in the list of chunk dictionaries, extracts the text from each chunk, and uses the `sentence-transformers` library to generate embeddings for each chunk. The function also constructs a new list of dictionaries that pair each embedding vector with its corresponding metadata, which can then be inserted into ChromaDB.
- *What I changed or overrode:*
The generated function was using manhattan distance for the embedding similarity search, which I changed to cosine similarity because it's more commonly used for text embeddings and generally provides better results in semantic search tasks.
