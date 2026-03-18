from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ApplicationEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    application_id: int
    event_type: str
    source: str
    old_status: str | None = None
    new_status: str | None = None
    message: str | None = None
    gmail_message_id: str | None = None
    created_at: datetime
    company: str | None = None
    position: str | None = None