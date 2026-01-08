
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class TaskBase(BaseModel):
    title: str
    content: str
    priority: str = "Medium"
    status: str = "Todo"
    due_date: Optional[date] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: int
    summary: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True
