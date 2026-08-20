from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ResearchProjectBase(BaseModel):
    name: str = Field(max_length=150)
    description: str | None = None


class ResearchProjectCreate(ResearchProjectBase):
    owner_id: int


class ResearchProjectUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=150)
    description: str | None = None
    owner_id: int | None = None


class ResearchProjectResponse(ResearchProjectBase):
    id: int
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)