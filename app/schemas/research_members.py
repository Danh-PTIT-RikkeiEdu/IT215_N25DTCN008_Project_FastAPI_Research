from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.models.research_members import MemberRole


class ResearchMemberBase(BaseModel):
    role: MemberRole = MemberRole.MEMBER


class ResearchMemberCreate(ResearchMemberBase):
    project_id: int
    user_id: int


class ResearchMemberUpdate(BaseModel):
    role: MemberRole | None = None


class ResearchMemberResponse(ResearchMemberBase):
    project_id: int
    user_id: int
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)