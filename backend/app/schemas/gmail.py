from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


GmailEventType = Literal[
    "in_review",
    "interview",
    "rejected",
    "accepted",
    "unknown",
]


class GmailParsedEventOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    gmail_message_id: str
    thread_id: str | None = None
    from_: str = Field(alias="from")
    subject: str
    date: datetime | None = None
    snippet: str | None = None
    event: GmailEventType
    reason: str | None = None