"""
CareerTwin AI – Chat Routes
GET    /api/chat/sessions                    – list sessions
POST   /api/chat/sessions                    – create session
GET    /api/chat/sessions/{session_id}       – get session with messages
DELETE /api/chat/sessions/{session_id}       – archive session
POST   /api/chat/sessions/{session_id}/send  – send message
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from database.session import get_db
from database.crud import (
    create_chat_session, get_chat_sessions,
    get_chat_session_with_messages, add_chat_message,
    get_profile,
)
from database.models import User, MessageRole
from utils.auth import get_current_user
from services.ai_service import career_chat

router = APIRouter()


class CreateSessionRequest(BaseModel):
    title: Optional[str] = "New Conversation"
    context_type: Optional[str] = "general"


class SendMessageRequest(BaseModel):
    message: str


@router.get("/sessions")
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    sessions = await get_chat_sessions(db, current_user.id)
    return {
        "sessions": [
            {
                "id": s.id,
                "title": s.title,
                "context_type": s.context_type,
                "updated_at": s.updated_at.isoformat(),
            }
            for s in sessions
        ]
    }


@router.post("/sessions")
async def create_session(
    payload: CreateSessionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = await create_chat_session(
        db=db,
        user_id=current_user.id,
        title=payload.title,
        context_type=payload.context_type,
    )
    return {"session_id": session.id, "title": session.title}


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = await get_chat_session_with_messages(db, session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {
        "id": session.id,
        "title": session.title,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "created_at": m.created_at.isoformat(),
            }
            for m in session.messages
        ],
    }


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = await get_chat_session_with_messages(db, session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    session.is_active = False
    return {"archived": True, "session_id": session_id}


@router.post("/sessions/{session_id}/send")
async def send_message(
    session_id: str,
    payload: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = await get_chat_session_with_messages(db, session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    # Build history for context
    history = [{"role": m.role, "content": m.content} for m in session.messages[-10:]]

    # Get user profile for personalisation
    profile = await get_profile(db, current_user.id)
    profile_dict = {
        "full_name": current_user.full_name,
        "career_goals": profile.career_goals if profile else "",
        "skills": profile.skills if profile else [],
        "branch": profile.branch if profile else "",
    }

    # Save user message
    await add_chat_message(db, session_id, MessageRole.USER, payload.message)

    # Get AI response
    ai_result = await career_chat(payload.message, history, profile_dict)
    reply = ai_result["reply"]
    tokens = ai_result["tokens_used"]

    # Save assistant message
    assistant_msg = await add_chat_message(db, session_id, MessageRole.ASSISTANT, reply, tokens)
    return {"message_id": assistant_msg.id, "reply": reply}
