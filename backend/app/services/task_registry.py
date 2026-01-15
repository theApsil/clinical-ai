from enum import Enum
from typing import Dict, Any


class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    ERROR = "error"


class TaskRegistry:
    def __init__(self):
        self._tasks: Dict[str, Dict[str, Any]] = {}

    def create(self, task_id: str):
        self._tasks[task_id] = {
            "status": TaskStatus.PENDING,
            "progress": 0,
            "result": None,
            "error": None,
        }

    def update(self, task_id: str, **kwargs):
        self._tasks[task_id].update(kwargs)

    def get(self, task_id: str) -> Dict[str, Any]:
        return self._tasks.get(task_id)
