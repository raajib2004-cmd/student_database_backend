# Student Database Backend with AI Chatbot

A modular FastAPI backend for managing student information, with an AI chatbot powered by **LangGraph** and **Google Gemini**. The chatbot uses a hybrid retrieval strategy: **SQL** for structured queries and **vector search** for semantic, meaning-based questions.

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.2-purple)](https://langchain-ai.github.io/langgraph/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](https://opensource.org/licenses/MIT)

---

## Overview

This project is a backend API that stores and retrieves student information, and exposes it through:

1. **REST CRUD endpoints** (`/students`) — create, read, update, delete student records.
2. **An AI chatbot endpoint** (`/chat`) — answers natural-language questions about students.

The chatbot never hallucinates student data: every fact it states comes from either the **structured database** (MariaDB via SQLAlchemy) or the **vector store** (Chroma, using Gemini embeddings). Gemini is only used to classify the question and to phrase the final natural-language answer.

---

## Features

- ✅ **Full CRUD API** for students with Pydantic validation
- ✅ **Automatic Swagger UI** at `/docs`
- ✅ **AI chatbot** built with LangGraph — a graph-based workflow with conditional routing
- ✅ **Hybrid retrieval**:
  - **SQL** for structured queries (IDs, names, CGPA, department, count)
  - **Vector search** for semantic queries (skills, interests, topics)
- ✅ **No-hallucination guarantee** — enforced by system prompt + tool-only answers
- ✅ **Docker + Docker Compose** for one-command deployment
- ✅ **26 automated tests** (pytest) covering CRUD, validation, chatbot behavior, and semantic search
- ✅ **Architecture, security, and design docs** under `docs/`

---

## Tech Stack

| Layer | Technology |
|---|---|
| API framework | FastAPI + Uvicorn |
| Validation | Pydantic v2 |
| Structured database | MariaDB (or MySQL) via SQLAlchemy |
| Vector database | Chroma (persistent, embedded) |
| Embeddings | Google Gemini `gemini-embedding-001` |
| Chat LLM | Google Gemini `gemini-3.1-flash-lite` |
| AI orchestration | LangGraph |
| Containerization | Docker + Docker Compose |
| Testing | pytest + FastAPI TestClient |
| Docs | Swagger / OpenAPI, Markdown |

---

## Architecture

```
                      ┌────────────────────┐
                      │   Client / User    │
                      └──────────┬─────────┘
                                 │ HTTP
                                 ▼
                      ┌────────────────────┐
                      │      FastAPI       │
                      │  /students, /chat  │
                      └──────────┬─────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                                     │
              ▼                                     ▼
      ┌───────────────┐                    ┌─────────────────┐
      │ CRUD Routes   │                    │  /chat Route    │
      │ (students.py) │                    │  (chat.py)      │
      └───────┬───────┘                    └────────┬────────┘
              │                                     │
              ▼                                     ▼
      ┌───────────────┐                    ┌─────────────────┐
      │ Service Layer │                    │   LangGraph     │
      │ (SQLAlchemy)  │                    │   Classifier    │
      └───────┬───────┘                    └────────┬────────┘
              │                                     │
              ▼                          ┌──────────┼───────────┐
      ┌───────────────┐                  ▼          ▼           ▼
      │   MariaDB     │◄───── SQL ──  db_node  semantic_node  general
      │  (students)   │                  │          │
      └───────────────┘                  │          │
                                         │          ▼
                                         │    ┌───────────┐
                                         │    │  Chroma   │
                                         │    │  vectors  │
                                         │    └─────┬─────┘
                                         │          │
                                         │          ▼
                                         │    Gemini Embeddings
                                         │          │
                                         └────┬─────┘
                                              ▼
                                     ┌─────────────────┐
                                     │     Gemini      │
                                     │  (final reply)  │
                                     └─────────────────┘
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for a deeper explanation, including when to use SQL vs. vector search.

---

## Project Structure

```
student_database_backend/
├── app/
│   ├── main.py                  # FastAPI entry point
│   ├── database/
│   │   └── connection.py        # SQLAlchemy engine + session
│   ├── models/
│   │   └── student.py           # Student ORM model
│   ├── schemas/
│   │   ├── student.py           # Pydantic schemas for students
│   │   └── chat.py              # Pydantic schemas for chatbot
│   ├── routes/
│   │   ├── students.py          # CRUD endpoints
│   │   └── chat.py              # Chatbot endpoint
│   ├── services/
│   │   └── student_service.py   # Business logic
│   └── chatbot/
│       ├── graph.py             # LangGraph workflow
│       ├── nodes.py             # Node functions
│       ├── tools.py             # DB tools + LangChain @tool wrappers
│       └── vector_store.py      # Chroma integration
├── docs/
│   ├── ARCHITECTURE.md
│   └── SECURITY.md
├── tests/
│   ├── conftest.py              # Pytest fixtures
│   ├── test_crud.py             # CRUD + validation tests
│   └── test_chatbot.py          # Chatbot integration tests
├── .dockerignore
├── .env.example                 # Safe template for environment variables
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Prerequisites

- **Python 3.11+**
- **MariaDB or MySQL** (XAMPP works fine — MariaDB is included)
- **Git**
- **Docker Desktop** (optional, for containerized deployment)
- A **Google Gemini API key** — free at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

---

## Quick Start (Docker)

The fastest way to run the whole stack:

```bash
# 1. Clone the repo
git clone https://github.com/raajib2004-cmd/student_database_backend.git
cd student_database_backend

# 2. Create .env from the template and add your Gemini key
cp .env.example .env
# (edit .env and set GEMINI_API_KEY=...)

# 3. Start the app + MariaDB together
docker compose up --build
```

Then visit:
- **Swagger UI**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/
- **Chatbot health**: http://localhost:8000/chat/health

To stop: press `Ctrl+C`, then `docker compose down`.

---

## Local Development (without Docker)

### 1. Install Python dependencies

```bash
python -m venv .venv
.venv\Scripts\activate.bat            # Windows
# source .venv/bin/activate            # macOS / Linux

pip install -r requirements.txt
```

### 2. Start MariaDB

- **XAMPP**: open the XAMPP Control Panel → click **Start** next to **MySQL**
- **Standalone MariaDB**: ensure the service is running

### 3. Create the database

```bash
# In a terminal:
mysql -u root -e "CREATE DATABASE IF NOT EXISTS student_db;"
# For XAMPP on Windows:
# C:\xampp\mysql\bin\mysql.exe -u root -e "CREATE DATABASE IF NOT EXISTS student_db;"
```

The `students` table is created automatically on app startup.

### 4. Configure `.env`

Copy the template and fill in your values:

```bash
cp .env.example .env
```

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | SQLAlchemy connection string, e.g., `mysql+pymysql://root:@localhost:3306/student_db` |
| `GEMINI_API_KEY` | Your Google Gemini API key |
| `APP_NAME` | Display name for the app |
| `DEBUG` | `True` for development |

> **Never commit `.env`** — it's listed in `.gitignore`.

### 5. Run the server

```bash
uvicorn app.main:app --reload
```

Open http://localhost:8000/docs.

---

## API Endpoints

### Students (CRUD)

| Method | Path | Description |
|---|---|---|
| POST | `/students` | Create a student |
| GET | `/students` | List students (paginated) |
| GET | `/students/{id}` | Get a student by internal id |
| PUT | `/students/{id}` | Update a student |
| DELETE | `/students/{id}` | Delete a student |

**Example — create a student:**

```bash
curl -X POST http://localhost:8000/students \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "S101",
    "name": "Rajib Das",
    "email": "rajib@example.com",
    "department": "CSE",
    "year": 3,
    "cgpa": 8.5,
    "bio": "Passionate about neural networks and AI research."
  }'
```

### Chatbot

| Method | Path | Description |
|---|---|---|
| POST | `/chat` | Ask the chatbot a question |
| GET | `/chat/health` | Check Gemini + Chroma status |

**Example — ask the chatbot:**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Who knows deep learning?"}'
```

Response:

```json
{
  "reply": "Rajib Das (S101) is the student who has expressed a passion for deep learning.",
  "category": "semantic_query"
}
```

---

## Chatbot Capabilities

The chatbot classifies every question into one of four categories:

| Category | Example | Data source |
|---|---|---|
| `greeting` | "Hello", "Thanks" | Canned response |
| `database_query` | "Show me S101", "How many CSE students?" | MariaDB (SQL) |
| `semantic_query` | "Who knows ML?", "Any mobile devs?" | Chroma (vector) |
| `general` | "What is 2+2?" | Gemini direct |

**Examples you can try:**

- *"Show me the details of student S101."*
- *"What is Rajib Das's CGPA?"*
- *"How many students are in the CSE department?"*
- *"Find students with CGPA above 8."*
- *"Who knows deep learning?"*
- *"Find students interested in mobile apps."*
- *"Anyone into robotics?"*
- *"Who is student ZZZ999?"* → replies "No student was found."

---

## Testing

The test suite has **26 tests** across two files.

```bash
pytest tests/ -v
```

- `tests/test_crud.py` — CRUD, validation, error handling (18 tests)
- `tests/test_chatbot.py` — classification, semantic search, no-hallucination guard (8 tests)

Tests run against a separate database (`student_db_test`) so your development data is untouched. Create it once:

```bash
mysql -u root -e "CREATE DATABASE IF NOT EXISTS student_db_test;"
```

> **Note:** Chatbot tests hit the live Gemini API. They're slower (~1 min total) and require `GEMINI_API_KEY` to be set. If the key isn't present, those tests are skipped automatically.

---

## Vector Database: Why Chroma?

The chatbot uses **Chroma** to store student-bio embeddings. Here's why it was chosen over alternatives:

| Option | Why Chroma wins for this project |
|---|---|
| **FAISS** | Chroma persists automatically and supports metadata |
| **Qdrant** | Chroma runs embedded (no server needed) |
| **Pinecone** | Chroma is local and free (no cloud account) |
| **Weaviate** | Chroma has simpler setup + native LangChain integration |

**Rule of thumb used in this project:**
- **SQL** for structured queries (exact IDs, counts, ranges)
- **Vector search** for meaning-based questions about free text

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for a fuller comparison.

---

## Security

- All secrets live in `.env` — **never committed**
- `.env.example` is the safe template
- Database connection strings are never hardcoded
- The chatbot does **not** leak PII (emails, phone numbers, addresses) unless explicitly asked
- Sensitive patterns are checked by scanning the repo for the Google API key prefix before each release

See [`docs/SECURITY.md`](docs/SECURITY.md) for the full model.

---

## Future Improvements

- [ ] JWT authentication and role-based access
- [ ] Rate limiting on `/chat`
- [ ] Background re-indexing of Chroma on student create/update
- [ ] Streaming responses from Gemini
- [ ] Support for multiple languages in the chatbot
- [ ] Prometheus metrics + Grafana dashboards
- [ ] CI/CD pipeline (GitHub Actions: lint, test, build, push image)
- [ ] Deployment to a cloud platform (Fly.io, Render, AWS)

---

## License

This project is licensed under the **MIT License**. See [LICENSE](https://opensource.org/licenses/MIT) for details.

---

## Author

**Rajib Das** — [github.com/raajib2004-cmd](https://github.com/raajib2004-cmd)

Built as an internship project demonstrating a production-style FastAPI + LangGraph + RAG backend.