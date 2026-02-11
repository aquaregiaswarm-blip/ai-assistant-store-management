"""Chat endpoint for the AI Agent."""
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json
import uuid

from ..agent.gm_agent import get_or_create_agent, clear_session
from ..database import get_db
from ..config import settings

router = APIRouter(prefix="/chat", tags=["chat"])

# Dataset prefix for BigQuery table references
DS = f"{settings.gcp_project_id}.{settings.bigquery_dataset}"


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    store_id: int = 1001


class ChatResponse(BaseModel):
    response: str
    session_id: str


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the AI agent and get a response."""
    session_id = request.session_id or str(uuid.uuid4())

    # Get store name
    db = get_db()
    store = db.query_one(
        f"SELECT Store_Name FROM `{DS}.Organization_Stores` WHERE Store_ID = @store_id",
        {"store_id": request.store_id}
    )

    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    store_name = store["Store_Name"]

    # Get or create agent
    agent = get_or_create_agent(session_id, request.store_id, store_name)

    # Get response
    response = agent.chat(request.message)

    return ChatResponse(
        response=response,
        session_id=session_id
    )


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """Stream a response from the AI agent."""
    session_id = request.session_id or str(uuid.uuid4())

    # Get store name
    db = get_db()
    store = db.query_one(
        f"SELECT Store_Name FROM `{DS}.Organization_Stores` WHERE Store_ID = @store_id",
        {"store_id": request.store_id}
    )

    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    store_name = store["Store_Name"]

    # Get or create agent
    agent = get_or_create_agent(session_id, request.store_id, store_name)

    def generate():
        # First yield the session_id
        yield f"data: {json.dumps({'type': 'session', 'session_id': session_id})}\n\n"

        # Stream the response
        for chunk in agent.chat_stream(request.message):
            yield f"data: {json.dumps({'type': 'text', 'content': chunk})}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Clear a chat session."""
    clear_session(session_id)
    return {"status": "ok", "message": "Session cleared"}


@router.get("/suggested-queries")
async def get_suggested_queries():
    """Get a list of suggested queries for the chat interface."""
    return [
        {
            "text": "How did we do yesterday?",
            "category": "performance"
        },
        {
            "text": "What was our peak hour?",
            "category": "performance"
        },
        {
            "text": "Any compliance issues I should know about?",
            "category": "compliance"
        },
        {
            "text": "Who's working today?",
            "category": "workforce"
        },
        {
            "text": "Who's my best linebuster?",
            "category": "operations"
        },
        {
            "text": "What are our top-selling items?",
            "category": "sales"
        },
        {
            "text": "How's our throughput compared to yesterday?",
            "category": "performance"
        },
        {
            "text": "Any minors approaching break time?",
            "category": "compliance"
        }
    ]
