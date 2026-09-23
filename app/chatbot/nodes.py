"""
LangGraph node functions for the chatbot.

Each node:
- Takes the graph state (a dict)
- Performs one task
- Returns a dict of the fields it updates

State keys we use:
  - question: the user's original question
  - category: "greeting" | "database_query" | "general"
  - context: any data retrieved (student info, etc.)
  - reply: the final natural-language reply
"""
import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# One shared LLM instance for all nodes.
# Note: gemini-3.6-flash uses fixed sampling defaults, so we don't pass `temperature`.
_llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
)


# ---------------------------------------------------------------------
# Helper: extract plain text from Gemini's response
# ---------------------------------------------------------------------
def _extract_text(content) -> str:
    """
    Gemini (via langchain-google-genai) sometimes returns content as:
    - a plain string, or
    - a list of content blocks, e.g., [{"type": "text", "text": "..."}]

    This helper always returns a clean string.
    """
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                # Common shapes: {"text": "..."} or {"type": "text", "text": "..."}
                text = block.get("text")
                if text:
                    parts.append(text)
        return " ".join(parts).strip()

    # Fallback for any other type
    return str(content).strip()


# ---------------------------------------------------------------------
# Node 1: Classify the question
# ---------------------------------------------------------------------
def classify_node(state: dict) -> dict:
    """
    Ask Gemini to classify the user's question into one of three categories.
    Returns: {"category": "..."}
    """
    question = state["question"]

    prompt = f"""Classify the following user question into exactly one of these categories:

- greeting       (hello, hi, thanks, good morning, how are you, etc.)
- database_query (asks about student records — names, IDs, CGPA, departments, counts, etc.)
- general        (everything else)

Respond with ONLY one word: greeting, database_query, or general.
Do not add punctuation or explanation.

Question: {question}
"""

    response = _llm.invoke(prompt)
    raw = _extract_text(response.content).lower()

    # Normalize to one of the three known categories
    if "greeting" in raw:
        category = "greeting"
    elif "database" in raw or "query" in raw:
        category = "database_query"
    else:
        category = "general"

    return {"category": category}


# ---------------------------------------------------------------------
# Node 2a: Handle greeting
# ---------------------------------------------------------------------
def greeting_node(state: dict) -> dict:
    """
    Return a friendly canned reply for greetings.
    Returns: {"reply": "..."}
    """
    return {
        "reply": (
            "Hello! I'm the Student Database Assistant. "
            "You can ask me things like: "
            "\"Show me student S101\", "
            "\"How many students are in CSE?\", or "
            "\"Find students with CGPA above 8.\""
        )
    }


# ---------------------------------------------------------------------
# Node 2b: Handle database query (Phase 6: placeholder; Phase 7: real DB)
# ---------------------------------------------------------------------
def database_query_node(state: dict) -> dict:
    """
    For Phase 6: return a placeholder response indicating DB access comes later.
    Phase 7: this will call the tools in tools.py to fetch real data.
    Returns: {"reply": "..."}
    """
    return {
        "reply": (
            "I can answer database questions about students, "
            "but the database connection for the chatbot is coming in the next phase. "
            "In the meantime, you can browse students at /students in the API."
        )
    }


# ---------------------------------------------------------------------
# Node 2c: Handle general questions
# ---------------------------------------------------------------------
def general_node(state: dict) -> dict:
    """
    For general questions, ask Gemini to answer directly.
    Returns: {"reply": "..."}
    """
    question = state["question"]

    prompt = (
        "You are a helpful assistant for a Student Database backend. "
        "Answer the following question in 2-3 sentences.\n\n"
        f"Question: {question}"
    )

    response = _llm.invoke(prompt)
    return {"reply": _extract_text(response.content)}


# ---------------------------------------------------------------------
# Node 3: Format the final reply
# ---------------------------------------------------------------------
def format_node(state: dict) -> dict:
    """
    Optional final pass — ensures the reply is clean and friendly.
    For Phase 6 we just pass it through; can be extended later.
    Returns: {} (no changes)
    """
    return {}