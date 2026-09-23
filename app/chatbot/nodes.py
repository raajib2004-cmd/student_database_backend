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
from langchain_core.messages import ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.chatbot.tools import ALL_TOOLS

load_dotenv()

# One shared LLM instance for all nodes.
# Note: gemini-3.6-flash uses fixed sampling defaults, so we don't pass `temperature`.
_llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
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
# Node 2b: Handle database query using Gemini + tools
# ---------------------------------------------------------------------
# We use a simple tool-calling loop:
#   1. Gemini sees the question + available tools.
#   2. Gemini picks a tool and args (with a unique call id).
#   3. We execute the tool and return a ToolMessage with the same call id.
#   4. Repeat until Gemini produces a final text answer.
# Max 5 iterations to avoid infinite loops.
# ---------------------------------------------------------------------

_SYSTEM_PROMPT = """You are a Student Database Assistant.

Your job is to answer questions about students using ONLY the provided tools.

Rules you MUST follow:
1. Use the tools to look up real student information from the database.
2. NEVER invent or guess student names, IDs, CGPAs, departments, or any other data.
3. If a tool returns no results, honestly tell the user that no matching students were found.
4. When listing multiple students, present the information clearly (bullet points).
5. Keep responses concise — one or two sentences plus any data list.
6. If the user asks something you cannot answer with these tools, say so politely.
"""


def database_query_node(state: dict) -> dict:
    """
    Handle a database-related question by letting Gemini call the tools
    in `app.chatbot.tools` and then phrasing the final answer.

    Returns: {"reply": "..."}
    """
    question = state["question"]

    # Bind the tools so Gemini can call them
    llm_with_tools = _llm.bind_tools(ALL_TOOLS)

    # Build the conversation: system prompt + user question
    messages = [
        ("system", _SYSTEM_PROMPT),
        ("human", question),
    ]

    # Loop: call Gemini, execute any tools it requests, feed results back.
    for _ in range(5):
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        # If Gemini didn't request any tools, it's done — return the text.
        tool_calls = getattr(response, "tool_calls", None) or []
        if not tool_calls:
            reply = _extract_text(response.content) or "I couldn't find a good answer."
            return {"reply": reply}

        # Execute each tool Gemini asked for
        for call in tool_calls:
            tool_name = call["name"]
            tool_args = call.get("args", {})
            tool_call_id = call["id"]

            matching = next((t for t in ALL_TOOLS if t.name == tool_name), None)
            if matching is None:
                messages.append(
                    ToolMessage(
                        content=f"Error: unknown tool '{tool_name}'",
                        tool_call_id=tool_call_id,
                    )
                )
                continue

            try:
                result = matching.invoke(tool_args)
            except Exception as e:
                result = f"Tool error: {e}"

            messages.append(
                ToolMessage(
                    content=f"{tool_name} returned: {result}",
                    tool_call_id=tool_call_id,
                )
            )

    # If we somehow exhausted the loop, return a friendly error
    return {
        "reply": (
            "I wasn't able to complete that lookup. "
            "Please try rephrasing your question."
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
    For now we just pass it through; can be extended later.
    Returns: {} (no changes)
    """
    return {}