"""Simple data models for Indra."""

import json
from enum import Enum
from typing import Dict, Any, List
from pydantic import BaseModel


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS" 
    DONE = "DONE"
    ERROR = "ERROR"


class Task(BaseModel):
    id: str
    task: str
    worker: str
    inputs: Dict[str, Any] = {}
    status: TaskStatus = TaskStatus.PENDING


class WorkerResult(BaseModel):
    task_id: str
    worker: str
    outputs: Dict[str, Any]


def validate_task_json(json_str: str) -> List[Task]:
    """Parse JSON string into Task objects."""
    data = json.loads(json_str)
    return [Task(**task_data) for task_data in data]