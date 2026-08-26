from app.db.database import Base
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum as SQLEnum # Để tránh lộn tên
from sqlalchemy.orm import relationship
from enum import Enum # Đảm bảo chỉ có những chức vụ được thêm sẵn
from datetime import datetime, timezone


class MemberRole(Enum):
    OWNER = "owner"
    MEMBER = "member"


class ResearchMembersModel(Base):
    __tablename__ = "research_members"

    role = Column(SQLEnum(MemberRole), default=MemberRole.MEMBER, nullable=False) # Mặc định làm member
    joined_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # User N–N Đề tài nghiên cứu qua ResearchMember
    project_id = Column(Integer, ForeignKey("research_projects.id", ondelete="CASCADE"), primary_key=True, )
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)

    research_project = relationship("ResearchProjectsModel", back_populates="research_members")
    user = relationship("UsersModel", back_populates="research_members")

    