from sqlalchemy.orm import Session

from app.models.application import Application
from app.schemas.application import ApplicationCreate, ApplicationUpdate
from app.models.application_event import ApplicationEvent

def _normalize_payload(data: dict) -> dict:
    if data.get("job_url") is not None:
        data["job_url"] = str(data["job_url"])
    return data


def list_applications(db: Session) -> list[Application]:
    return db.query(Application).order_by(Application.created_at.desc()).all()


def get_application(db: Session, application_id: int) -> Application | None:
    return db.query(Application).filter(Application.id == application_id).first()


def create_application(db: Session, payload: ApplicationCreate) -> Application:
    data = _normalize_payload(payload.model_dump())
    obj = Application(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_application(db: Session, obj: Application, payload: ApplicationUpdate) -> Application:
    old_status = obj.status

    if payload.company is not None:
        obj.company = payload.company

    if payload.position is not None:
        obj.position = payload.position

    if payload.status is not None:
        obj.status = payload.status

    if payload.location is not None:
        obj.location = payload.location

    if payload.notes is not None:
        obj.notes = payload.notes

    if payload.job_url is not None:
        obj.job_url = payload.job_url

    # 🔥 лог изменения статуса
    if old_status != obj.status:
        db.add(
            ApplicationEvent(
                application_id=obj.id,
                event_type="manual_status_change",
                source="manual",
                old_status=old_status,
                new_status=obj.status,
                message="Status changed manually by user",
                gmail_message_id=None,
            )
        )

    db.commit()
    db.refresh(obj)
    return obj


def delete_application(db: Session, obj: Application) -> None:
    db.delete(obj)
    db.commit()