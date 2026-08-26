from app.db.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import timezone, datetime
from enum import Enum


class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ResearchTasksModel(Base):
    __tablename__ = "research_tasks"

    id = Column(Integer, index=True, primary_key=True, autoincrement=True)
    title = Column(String(150), index=True, nullable=False)  
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.TODO, nullable=False)
    priority = Column(SQLEnum(TaskPriority), default=TaskPriority.LOW, nullable=False)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Đề tài nghiên cứu 1–N Nhiệm vụ nghiên cứu
    project_id = Column(Integer, ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False)
    research_project = relationship("ResearchProjectsModel", back_populates="research_tasks")

    # User 1–N Nhiệm vụ nghiên cứu (assignee).
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("UsersModel", back_populates="research_tasks")