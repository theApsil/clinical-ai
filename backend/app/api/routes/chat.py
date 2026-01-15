from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.deps import get_session
from app.logger import logger
router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    session_id: str
    message: str


@router.post("/")
def chat(req: ChatRequest):
    try:
        dialog = get_session(req.session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")

    response = dialog.handle_message(req.message)
    return response
