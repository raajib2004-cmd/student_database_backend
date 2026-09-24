"""
Chatbot integration tests.

These tests hit the REAL Gemini API, so they:
- Require GEMINI_API_KEY to be set (otherwise they're skipped)
- Are slower (a few seconds each)
- Can hit free-tier rate limits if run too fast

They verify:
- Classification routes the question to the right category
- The no-hallucination guarantee (unknown student → "not found")
- Semantic search finds the right student by meaning
- The /chat/health endpoint reports OK
"""
import os

import pytest

# Skip the entire module if GEMINI_API_KEY is not configured
pytestmark = pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY is not set — chatbot tests require a live Gemini key.",
)


# ---------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------
def test_chat_health(client):
    response = client.get("/chat/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("ok", "degraded")
    # Gemini and Chroma should both be reachable in a working setup
    assert data["gemini"] == "ok"


# ---------------------------------------------------------------------
# Classification (via the /chat endpoint)
# ---------------------------------------------------------------------
def test_classify_greeting(client):
    response = client.post("/chat", json={"message": "Hello!"})
    assert response.status_code == 200
    assert response.json()["category"] == "greeting"


def test_classify_database_query(client, sample_student):
    client.post("/students", json=sample_student)
    response = client.post("/chat", json={"message": "Show me student T001."})
    assert response.status_code == 200
    assert response.json()["category"] == "database_query"


def test_classify_semantic_query(client):
    response = client.post("/chat", json={"message": "Who knows machine learning?"})
    assert response.status_code == 200
    assert response.json()["category"] == "semantic_query"


# ---------------------------------------------------------------------
# The golden rule: no hallucination
# ---------------------------------------------------------------------
def test_unknown_student_returns_not_found(client):
    """The chatbot must NOT invent a student for a nonexistent ID."""
    response = client.post("/chat", json={"message": "Show me student ZZZ999."})
    assert response.status_code == 200
    data = response.json()
    reply_lower = data["reply"].lower()
    # The reply should indicate the student wasn't found — not make one up
    assert any(
        phrase in reply_lower
        for phrase in ["not found", "no student", "couldn't find", "could not find", "no matching"]
    )


# ---------------------------------------------------------------------
# Semantic search through the chatbot
# ---------------------------------------------------------------------
def test_semantic_search_finds_right_student(client):
    """
    Add a student with a distinctive bio, then ask about the topic using
    words that don't appear in the bio.
    """
    payload = {
        "student_id": "SEM01",
        "name": "Semantic Student",
        "email": "semantic@example.com",
        "department": "CSE",
        "year": 2,
        "cgpa": 8.0,
        "bio": "Enjoys neural networks, deep learning, and AI research.",
    }
    client.post("/students", json=payload)

    # Note: this test depends on the student being indexed into Chroma.
    # The API doesn't auto-index on create (yet) — so this test verifies
    # the semantic path is reachable; the student will be picked up
    # after the next `reindex_all()` call.

    from app.chatbot.vector_store import reindex_all
    reindex_all()

    response = client.post("/chat", json={"message": "Who knows machine learning?"})
    assert response.status_code == 200
    assert response.json()["category"] == "semantic_query"
    # The reply should mention the student who likes neural networks
    assert "semantic" in response.json()["reply"].lower() or "neural" in response.json()["reply"].lower()


# ---------------------------------------------------------------------
# Validation on the /chat endpoint itself
# ---------------------------------------------------------------------
def test_chat_empty_message_rejected(client):
    response = client.post("/chat", json={"message": ""})
    assert response.status_code == 422


def test_chat_missing_message_rejected(client):
    response = client.post("/chat", json={})
    assert response.status_code == 422