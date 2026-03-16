from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.application import ApplicationCreate, ApplicationOut, ApplicationUpdate
from app.services.application_service import (
    create_application,
    delete_application,
    get_application,
    list_applications,
    update_application,
)

router = APIRouter(prefix="/applications", tags=["applications"])


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