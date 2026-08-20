from app.db.database import Base
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import timezone, datetime


class ResearchProjectsModel(Base):
    __tablename__ = "research_projects"

    id = Column(Integer, index=True, primary_key=True, autoincrement=True)
    name = Column(String(150), index=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # User 1–N Đề tài nghiên cứu (owner)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("UsersModel", back_populates="research_projects")

    # Đề tài nghiên cứu 1–N Nhiệm vụ nghiên cứu
    research_tasks = relationship("ResearchTasksModel", back_populates="research_project")

    # User N–N Đề tài nghiên cứu qua ResearchMember
    research_members = relationship("ResearchMembersModel", back_populates="research_project")

    