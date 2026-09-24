"""
HTTP route for the chatbot.

Exposes:
- POST /chat        — run the LangGraph workflow and return a natural-language reply.
- GET  /chat/health — verify Gemini and Chroma are reachable.
"""
from fastapi import APIRouter, HTTPException, status

from app.chatbot.graph import ask
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(
    prefix="/chat",
    tags=["Chatbot"],
)


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask the chatbot a question",
    description=(
        "Send a message to the Student Database chatbot.\n\n"
        "The chatbot classifies the question as one of:\n"
        "- `greeting` — hello, thanks, etc.\n"
        "- `database_query` — structured lookups (ID, name, CGPA, department, count)\n"
        "- `semantic_query` — skills / interests / topics (uses vector search over bios)\n"
        "- `general` — anything else\n\n"
        "Then it routes the question to the right handler and returns a natural-language reply.\n\n"
        "**The chatbot never invents student data** — all facts come from the database or vector store."
    ),
    responses={
        500: {"description": "Unexpected error while processing the question"},
    },
)
def chat(payload: ChatRequest):
    """Run the chatbot graph for a single question."""
    try:
        result = ask(payload.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chatbot error: {e}",
        )

    return ChatResponse(
        reply=result["reply"],
        category=result["category"],
    )


# ---------------------------------------------------------------------
# Health endpoint for the chatbot dependencies
# ---------------------------------------------------------------------
@router.get(
    "/health",
    summary="Check chatbot dependencies",
    description=(
        "Verifies that the Gemini API and the Chroma vector store are reachable.\n\n"
        "Returns `ok` if both are working, `degraded` otherwise."
    ),
)
def chat_health():
    """
    Quick health check for the chatbot stack.

    - Pings Gemini with a tiny prompt.
    - Pings Chroma with a tiny vector search.
    """
    from app.chatbot.nodes import _llm
    from app.chatbot.vector_store import semantic_search

    status_report = {
        "gemini": "unknown",
        "chroma": "unknown",
    }

    # Check Gemini
    try:
        _llm.invoke("ping")
        status_report["gemini"] = "ok"
    except Exception as e:
        status_report["gemini"] = f"error: {e}"

    # Check Chroma
    try:
        semantic_search("test", k=1)
        status_report["chroma"] = "ok"
    except Exception as e:
        status_report["chroma"] = f"error: {e}"

    overall = (
        "ok"
        if status_report["gemini"] == "ok" and status_report["chroma"] == "ok"
        else "degraded"
    )

    return {"status": overall, **status_report}