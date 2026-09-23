"""
HTTP route for the chatbot.

Exposes POST /chat which runs the LangGraph workflow and returns
a natural-language reply plus the detected category.
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
        "The chatbot classifies the question as `greeting`, `database_query`, or `general`, "
        "routes it through the appropriate handler, and returns a natural-language reply.\n\n"
        "**Note:** In this phase, database queries return a placeholder message. "
        "Real database integration comes in the next phase."
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