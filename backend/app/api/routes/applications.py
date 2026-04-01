from datetime import datetime
import csv
import io
import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.application import Application
from app.models.application_event import ApplicationEvent
from app.schemas.application import ApplicationCreate, ApplicationOut, ApplicationUpdate
from app.services.application_service import (
    create_application,
    delete_application,
    get_application,
    list_applications,
    update_application,
)

router = APIRouter(prefix="/applications", tags=["applications"])


def serialize_application(app: Application) -> dict:
    return {
        "id": app.id,
        "company": app.company,
        "position": app.position,
        "location": app.location,
        "status": app.status,
        "applied_date": app.applied_date.isoformat() if app.applied_date else None,
        "job_url": app.job_url,
        "notes": app.notes,
        "created_at": app.created_at.isoformat() if app.created_at else None,
        "updated_at": app.updated_at.isoformat() if app.updated_at else None,
    }


def serialize_event(event: ApplicationEvent) -> dict:
    return {
        "id": event.id,
        "application_id": event.application_id,
        "event_type": event.event_type,
        "source": event.source,
        "old_status": event.old_status,
        "new_status": event.new_status,
        "message": event.message,
        "gmail_message_id": event.gmail_message_id,
        "created_at": event.created_at.isoformat() if event.created_at else None,
    }


def get_filtered_applications(db: Session, status_filter: str | None) -> list[Application]:
    query = db.query(Application)

    if status_filter and status_filter != "all":
        query = query.filter(Application.status == status_filter)

    return query.order_by(Application.created_at.desc()).all()


@router.get("/export/json")
def export_applications_json(
    status_filter: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    applications = get_filtered_applications(db, status_filter)

    payload = {
        "meta": {
            "type": "applications_export",
            "format": "json",
            "version": 1,
            "exported_at": datetime.utcnow().isoformat() + "Z",
            "filter": status_filter or "all",
            "count": len(applications),
        },
        "applications": [serialize_application(app) for app in applications],
    }

    filename = f"applyflow_applications_{status_filter or 'all'}.json"

    return Response(
        content=json.dumps(payload, ensure_ascii=False, indent=2),
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.get("/export/csv")
def export_applications_csv(
    status_filter: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    applications = get_filtered_applications(db, status_filter)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(
        [
            "id",
            "company",
            "position",
            "location",
            "status",
            "applied_date",
            "job_url",
            "notes",
            "created_at",
            "updated_at",
        ]
    )

    for app in applications:
        writer.writerow(
            [
                app.id,
                app.company,
                app.position,
                app.location or "",
                app.status,
                app.applied_date.isoformat() if app.applied_date else "",
                app.job_url or "",
                app.notes or "",
                app.created_at.isoformat() if app.created_at else "",
                app.updated_at.isoformat() if app.updated_at else "",
            ]
        )

    filename = f"applyflow_applications_{status_filter or 'all'}.csv"

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.get("/export/backup")
def export_full_backup(db: Session = Depends(get_db)):
    applications = db.query(Application).order_by(Application.created_at.desc()).all()
    events = db.query(ApplicationEvent).order_by(ApplicationEvent.created_at.desc()).all()

    payload = {
        "meta": {
            "type": "applyflow_backup",
            "format": "json",
            "version": 1,
            "exported_at": datetime.utcnow().isoformat() + "Z",
            "applications_count": len(applications),
            "events_count": len(events),
        },
        "applications": [serialize_application(app) for app in applications],
        "events": [serialize_event(event) for event in events],
    }

    filename = f"applyflow_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"

    return Response(
        content=json.dumps(payload, ensure_ascii=False, indent=2),
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.get("", response_model=list[ApplicationOut])
def get_all_applications(db: Session = Depends(get_db)):
    return list_applications(db)


@router.post("", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
def create_new_application(payload: ApplicationCreate, db: Session = Depends(get_db)):
    return create_application(db, payload)


@router.get("/{application_id}", response_model=ApplicationOut)
def get_one_application(application_id: int, db: Session = Depends(get_db)):
    obj = get_application(db, application_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Application not found")
    return obj


@router.patch("/{application_id}", response_model=ApplicationOut)
def patch_application(application_id: int, payload: ApplicationUpdate, db: Session = Depends(get_db)):
    obj = get_application(db, application_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Application not found")
    return update_application(db, obj, payload)


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_application(application_id: int, db: Session = Depends(get_db)):
    obj = get_application(db, application_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Application not found")
    delete_application(db, obj)
    return None