# Student Database Backend — Architecture


---

## When to Use SQL vs. Vector Search

The chatbot routes questions into **four categories**:

| Category | Example question | Handler | Data source |
|---|---|---|---|
| `greeting` | "Hello", "Thanks" | Canned response | None |
| `database_query` | "Show me S101", "How many CSE students?" | SQL tools | MariaDB |
| `semantic_query` | "Who knows ML?", "Anyone into mobile apps?" | Vector tools | Chroma |
| `general` | "What is 2+2?" | Gemini direct answer | None |

### Decision Rules

| If the question mentions… | Use SQL | Use Vector |
|---|---|---|
| A specific `student_id` (S101) | ✅ | |
| A student's name | ✅ | |
| A numeric field (CGPA, year) | ✅ | |
| A count ("how many") | ✅ | |
| A department filter | ✅ | |
| A skill, interest, hobby, topic | | ✅ |
| A vague concept ("ML", "backend", "robotics") | | ✅ |
| A synonym-heavy question ("deep learning" ≈ "neural networks") | | ✅ |

**Rule of thumb:**
- **Structured data** → SQL (exact match, fast, deterministic)
- **Meaning-based questions about free text** → Vector search (semantic similarity)

---

## The Golden Rule: No Hallucination

The chatbot **must never invent student data**. This is enforced by:

1. **System prompt** — explicitly tells Gemini: *"Only state facts that appear in tool outputs."*
2. **Tool-only answers** — Gemini must call a tool to fetch data before answering.
3. **No context dumping** — Gemini never sees the full student table, only tool results.
4. **Explicit not-found handling** — if a tool returns nothing, Gemini must say "no students found."

Test case: `"Who is student S999?"` (nonexistent) → chatbot says "No student was found."

---

## Vector Database Choice: Chroma

| Option | Why we didn't pick it | Why Chroma wins |
|---|---|---|
| **FAISS** | Manual persistence, no metadata filtering | Chroma persists automatically |
| **Qdrant** | Requires running a Docker server | Chroma runs embedded |
| **Pinecone** | Cloud-only, requires account + API key | Chroma is local and free |
| **Weaviate** | Complex setup (Docker + GraphQL) | Chroma has native LangChain integration |

**Chroma is chosen because:**
- ✅ Zero infrastructure (embedded, `pip install`)
- ✅ Persistent on disk (`./chroma_data/`)
- ✅ Native LangChain integration
- ✅ Free and open source
- ✅ Handles thousands of vectors comfortably

For *millions* of student records, Qdrant or Pinecone would be better. For this project — internship scale — Chroma is the right tool.

---

## Graph Nodes Explained

| Node | Purpose | Input | Output |
|---|---|---|---|
| `classify_node` | Ask Gemini to categorize the question | `question` | `category` |
| `greeting_node` | Return canned greeting reply | — | `reply` |
| `database_query_node` | Gemini calls SQL tools, phrases answer | `question` | `reply` |
| `semantic_query_node` | Gemini calls vector tools, phrases answer | `question` | `reply` |
| `general_node` | Gemini answers directly | `question` | `reply` |
| `format_node` | (Pass-through, reserved for future) | — | — |

Each node returns a dict that LangGraph merges into the shared state.

---

## Technology Stack

| Layer | Technology |
|---|---|
| API framework | FastAPI + Uvicorn |
| Validation | Pydantic v2 |
| Database (structured) | MariaDB (via XAMPP) + SQLAlchemy |
| Vector database | Chroma |
| Embeddings | Google Gemini `gemini-embedding-001` |
| Chat LLM | Google Gemini `gemini-3.1-flash-lite` |
| Graph framework | LangGraph |
| Containerization | Docker (Phase 12) |

---

## Security

- All secrets (DB credentials, API keys) live in `.env` — **never committed**.
- `.env` is in `.gitignore`; `.env.example` is the safe template.
- No API key present in any tracked file (verified with `git grep "AIzaSy" HEAD`).
- The chatbot does not echo sensitive fields unless explicitly asked.

---

## Testing Strategy

| Layer | Test type | Coverage |
|---|---|---|
| CRUD APIs | Unit tests via FastAPI TestClient | Create / Read / Update / Delete + validation |
| Chatbot classification | Integration tests | Each category → correct node |
| Tool calling | Integration tests | Gemini calls right tools for right questions |
| Semantic search | Integration tests | Chroma returns correct students |
| Hallucination guard | Integration test | Unknown student → "not found" message |

See `tests/` (added in Phase 11).
---

## High-Level Flow
