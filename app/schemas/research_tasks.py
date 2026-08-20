from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.research_tasks import TaskPriority, TaskStatus


class ResearchTaskBase(BaseModel):
    title: str = Field(max_length=150)
    description: str | None = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.LOW
    due_date: datetime | None = None


class ResearchTaskCreate(ResearchTaskBase):
    project_id: int
    assignee_id: int | None = None


class ResearchTaskUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=150)
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: datetime | None = None
    project_id: int | None = None
    assignee_id: int | None = None


class ResearchTaskResponse(ResearchTaskBase):
    id: int
    project_id: int
    assignee_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)