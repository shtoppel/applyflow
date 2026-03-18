from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_db
from app.models.application_event import ApplicationEvent
from app.schemas.application_event import ApplicationEventOut

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/recent", response_model=list[ApplicationEventOut])
def get_recent_events(db: Session = Depends(get_db)):
    events = db.execute(
        select(ApplicationEvent)
        .options(joinedload(ApplicationEvent.application))
        .order_by(ApplicationEvent.created_at.desc())
        .limit(20)
    ).scalars().all()

    result = []
    for event in events:
        result.append(
            ApplicationEventOut(
                id=event.id,
                application_id=event.application_id,
                event_type=event.event_type,
                source=event.source,
                old_status=event.old_status,
                new_status=event.new_status,
                message=event.message,
                gmail_message_id=event.gmail_message_id,
                created_at=event.created_at,
                company=event.application.company if event.application else None,
                position=event.application.position if event.application else None,
            )
        )

    return result