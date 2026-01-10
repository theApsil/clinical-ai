from typing import Dict
from uuid import uuid4

from app.services.dialog_manager import DialogManager

# TODO: Привязка к Postgres
DIALOG_SESSIONS: Dict[str, DialogManager] = {}


def create_session(dialog_manager: DialogManager) -> str:
    session_id = str(uuid4())
    DIALOG_SESSIONS[session_id] = dialog_manager
    return session_id


def get_session(session_id: str) -> DialogManager:
    if session_id not in DIALOG_SESSIONS:
        raise KeyError("Session not found")
    return DIALOG_SESSIONS[session_id]
