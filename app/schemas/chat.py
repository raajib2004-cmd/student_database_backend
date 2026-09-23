"""
Pydantic schemas for the chatbot endpoints.
"""
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming chat request from the client."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="The user's question or message.",
        examples=["Show me the details of student S101."],
    )


class ChatResponse(BaseModel):
    """Response returned by the chatbot."""

    reply: str = Field(
        ...,
        description="The chatbot's natural-language reply.",
    )
    category: str = Field(
        ...,
        description="How the question was classified (greeting / database_query / general).",
    )