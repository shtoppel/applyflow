from sqlalchemy.orm import Session

from app.models.application import Application
from app.schemas.application import ApplicationCreate, ApplicationUpdate


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
    data = _normalize_payload(payload.model_dump(exclude_unset=True))
    for key, value in data.items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_application(db: Session, obj: Application) -> None:
    db.delete(obj)
    db.commit()