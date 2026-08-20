from app.db.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import timezone, datetime
from enum import Enum


class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"


class UsersModel(Base):
    __tablename__ = "users"

    id = Column(Integer, index=True, primary_key=True, autoincrement=True)
    email = Column(String(255), index=True, unique=True, nullable=False)  # 1 Email dài tối đa 254 ký tự nên để luôn là 255 cho dễ tính
    password_hash = Column(String(60), nullable=False) # Độ dài mật khẩu được băm từ bcrypt là 60 nên để vậy là tối ưu nhất cho truy vấn DB
    full_name = Column(String(100), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # User 1–N Đề tài nghiên cứu (owner)
    research_projects = relationship("ResearchProjectsModel", back_populates="user")

    # User 1–N Nhiệm vụ nghiên cứu (assignee).
    research_tasks = relationship("ResearchTasksModel", back_populates="user")

    # User N–N Đề tài nghiên cứu qua ResearchMember
    research_members = relationship("ResearchMembersModel", back_populates="user")