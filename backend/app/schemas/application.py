from datetime import date, datetime
from pydantic import BaseModel, Field, HttpUrl


class ApplicationBase(BaseModel):
    company: str = Field(min_length=1, max_length=255)
    position: str = Field(min_length=1, max_length=255)
    location: str | None = Field(default=None, max_length=255)
    status: str = "draft"
    applied_date: date | None = None
    job_url: HttpUrl | None = None
    notes: str | None = None


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    company: str | None = Field(default=None, min_length=1, max_length=255)
    position: str | None = Field(default=None, min_length=1, max_length=255)
    location: str | None = Field(default=None, max_length=255)
    status: str | None = None
    applied_date: date | None = None
    job_url: HttpUrl | None = None
    notes: str | None = None


class ApplicationOut(ApplicationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}