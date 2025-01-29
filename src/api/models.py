from datetime import datetime
from pydantic import BaseModel
import uuid
from typing import Optional

class TaskStatus:
    def __init__(self):
        self.id: str = str(uuid.uuid4())
        self.status: str = "pending"  # pending, processing, completed, failed
        self.progress: int = 0
        self.result_path: Optional[str] = None
        self.error: Optional[str] = None
        self.created_at: datetime = datetime.now()

class TaskResponse(BaseModel):
    task_id: str

class TaskStatusResponse(BaseModel):
    status: str
    progress: int
    error: Optional[str] = None 