from typing import Dict, Optional
from threading import Lock

_tasks: Dict[str, dict] = {}
_lock = Lock()


def create_task(task_id: str):
    with _lock:
        _tasks[task_id] = {
            "status": "processing",
            "progress": 0,
            "session_id": None,
            "error": None,
        }


def update_task(task_id: str, **kwargs):
    with _lock:
        if task_id in _tasks:
            _tasks[task_id].update(kwargs)


def get_task(task_id: str) -> Optional[dict]:
    with _lock:
        return _tasks.get(task_id)
