from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...schemas.contracts import ApplicationRead, StatusUpdate
from ...services.hiring import update_status


router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.patch("/{application_id}/status", response_model=ApplicationRead)
def change_status(application_id: int, data: StatusUpdate, db: Session = Depends(get_db)):
    return update_status(db, application_id, data.status.value, data.note)

