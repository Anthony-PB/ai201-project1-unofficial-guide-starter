# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

The domain I chose is Unofficial Guide to CS Courses at Cornell. This knowledge is valuable because it provides extra insight and information about CS courses from the perspective of students who have actually take the courses. Official course rosters only give prerequisites and dry descriptions. They don't tell you the actual project workloads, which professors give the best feedback, or how brutal the weekly problem sets are.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| #   | Source                   | Description                                                                                                                          | URL or location                                                                             |
| --- | ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| 1   | r/Cornell                | Comments on the difficulty of CS3110                                                                                                 | https://www.reddit.com/r/Cornell/comments/ag1yav/deleted_by_user/ and difficulty_cS3110.txt                          |
| 2   | r/Cornell                | Describes the difficulty of CS2800 and CS3110                                                                                        | https://www.reddit.com/r/Cornell/comments/1q2brio/how_hard_is_cs_3110_and_cs_2800_actually/ and CS2800_CS3110.txt |
| 3   | r/Cornell                | Making the correct choice for the probability theory prerequisite for CS4780                                                         | https://www.reddit.com/r/Cornell/comments/vhk16k/cs4780_introduction_to_machine_learning/ and  prob_prereq.txt |
| 4   | r/Cornell                | Listing out and reviewing cs electives                                                                                               | https://www.reddit.com/r/Cornell/comments/10mrbgs/bestmost_useful_cs_electives/   and best_electives.txt          |
| 5   | r/Cornell                | Comments answering how useful courses are for the industry and where should a student's focus be in order to maximize their learning | https://www.reddit.com/r/Cornell/comments/gls928/cs_honest_questions/       and honest.txt                |
| 6   | GitLab                   | FAQ from a peer-maintained directory providing general information on all cs courses                                                 | https://cornellcswiki.gitlab.io/faq.html                                                    |
| 7   | CUReviews                | Aggregated student reviews of the CS4780 course                                                                                      | https://www.cureviews.org/course/CS/4780                                                    |
| 8   | General Prereqs          | Table showing the general idea of courses that a CS Major should take                                                                | data/cs.txt                                                                                 |
| 9   | Cornell Academic Catalog | Official BS in Computer Science requirements, affiliation GPA cutoffs, and Honors program rules.                                     | https://catalog.cornell.edu/programs/computer-science-bs/        or data/catalog.txt                           |
| 10  | Engineering Handbook     | Official course checklist detailing CS core requirements, credit minimums, and prerequisites.                                        | data/engineering_handbook.txt                                                               |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**
450 Chars
**Overlap:**
75 Chars
**Reasoning:**
My corpus mixes short Reddit opinions (1–3 sentences) with longer FAQ and handbook text. 450 characters captures a complete review thought without merging unrelated opinions. 75-character overlap ensures facts that straddle a boundary (e.g., a course name in one sentence, the opinion in the next) appear in at least one complete chunk.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**
all-MiniLM-L6-v2 via sentence-transformers. This model is a good balance of performance and speed for general English text, which fits my Reddit and FAQ documents.
**Top-k:**
 k=4. This is a good starting point to capture multiple perspectives without overwhelming the generation stage. It allows for a mix of opinions and facts while keeping the context manageable for the LLM.
**Production tradeoff reflection:**
Different embedding model -> A more powerful model like a fine-tuned BERT variant could improve accuracy on domain-specific language (e.g., course names, CS jargon) but would increase latency and cost. In a real deployment, I would consider the user experience more heavily and might opt for a faster model as users would expect quick responses.
Token limit -> If I had a larger token limit for the generation stage, I could retrieve more chunks (e.g., top-10) to provide a richer context and more diverse opinions. However, this would also increase the chance of including irrelevant information, so I would need to balance quantity with relevance.
---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| #   | Question | Expected answer |
| --- | -------- | --------------- |
| 1   |    What do students say about the difficulty of problem sets in CS3110?      |         Students describe CS3110 as having challenging weekly OCaml problem sets; some students call it one of the hardest required CS courses        |
| 2   |     What are the most commonly recommended CS electives for students interested in ML/AI?     |         CS4780, CS4782, and CS4787 are frequently mentioned4What are the minimum GPA requirements to affiliate with the CS major at Cornell Engineering?Students must maintain a certain GPA in core courses; the official catalog states specific cutoffs5What do students say about the workload and project structure in CS4780?Students note heavy theoretical content and programming projects; CUReviews comments reflect mixed opinions on difficulty        |
| 3   |    What courses do students recommend as prerequisites before taking CS4780?      |        Students recommend taking a solid probability course (like MATH 4710 or ECE 3100) before CS4780         |
| 4   |     What are the minimum GPA requirements to affiliate with the CS major at Cornell Engineering?     |         to affiliate with the CS major at Cornell Engineering?Students must maintain a certain GPA in core courses; the official catalog states specific cutoffs, C is the absolute minimum generally but there are grouped courses that need a higher average gpa     |
| 5   |     What do students say about the workload and project structure in CS4780?     |        Students note heavy theoretical content and programming projects; CUReviews comments reflect mixed opinions on difficulty         |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. Reddit thread noise: Reddit posts contain off-topic tangents, memes, and deleted comments. Chunks from these may embed poorly and surface for unrelated queries, e.g., a chunk about campus dining appearing when asked about CS3110 workload. I believe this is already present in some of the documents.

2. Chunk boundary splits: A review might name a course in one sentence and give the opinion in the next. If those land in separate chunks with no overlap, neither chunk alone answers the query correctly. The 75-char overlap mitigates this but doesn't eliminate it.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

Raw Documents (Reddit, CUReviews, txt files)
|
v
[Document Ingestion — Python / pdfplumber / requests]
|
v
[Chunking — LangChain RecursiveCharacterTextSplitter, 450 chars, 75 overlap]
|
v
[Embedding — sentence-transformers all-MiniLM-L6-v2]
|
v
[Vector Store — ChromaDB (local)]
|
v
[Retrieval — ChromaDB semantic search, top-k=4]
|
v
[Generation — Groq llama-3.3-70b-versatile]
|
v
[Query Interface — Gradio web UI]

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**
I'll give Claude my Documents table and Chunking Strategy section and ask it to implement a load_and_chunk() function that reads from my local .txt files and URLs, cleans HTML/navigation text, and produces chunks of 450 chars with 75-char overlap. I'll verify by printing 5 random chunks and checking they're readable, self-contained, and free of HTML artifacts. If some urls are too complex to scrape, I'll adjust the function to handle them or exclude them from the corpus. (Or simply convert them to .txt files myself and read those instead.)
**Milestone 4 — Embedding and retrieval:**
I'll give Claude my Architecture diagram and Retrieval Approach section and ask it to implement embed_chunks() (loads chunks, embeds with MiniLM, stores in ChromaDB with source metadata) and retrieve() (takes a query string, returns top-4 chunks with source names). I'll verify by running 3 of my eval questions and checking that distance scores are below 0.5 and returned chunks are visibly relevant.
**Milestone 5 — Generation and interface:**
I'll give Claude my grounding requirement ("answer only from retrieved context, cite sources") and ask it to implement ask() (takes query → retrieves chunks → builds prompt → calls Groq → returns answer + sources) and a Gradio interface wiring ask() to an input box and two output boxes (answer, sources). I'll verify grounding by asking an out-of-scope question and confirming the system says it doesn't have enough information rather than hallucinating.