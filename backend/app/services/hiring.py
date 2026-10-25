from datetime import date

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from ..core.errors import ApiError
from ..models.entities import Application, Job, StatusHistory
from ..schemas.contracts import ApplicationCreate, JobCreate


ALLOWED_TRANSITIONS = {
    "pending": {"shortlisted", "rejected"},
    "shortlisted": {"offered", "rejected"},
    "offered": {"rejected"},
    "rejected": set(),
}


def application_count(db: Session, job_id: int) -> int:
    return db.scalar(select(func.count(Application.id)).where(Application.job_id == job_id)) or 0


def job_payload(db: Session, job: Job) -> dict:
    count = application_count(db, job.id)
    cap_available = job.max_applicants is None or count < job.max_applicants
    return {
        **{column.name: getattr(job, column.name) for column in Job.__table__.columns},
        "application_count": count,
        "accepting_applications": not job.is_closed and job.deadline >= date.today() and cap_available,
    }


def create_job(db: Session, data: JobCreate) -> Job:
    payload = data.model_dump()
    payload["location"] = data.location.value
    job = Job(**payload)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_job_or_404(db: Session, job_id: int) -> Job:
    job = db.get(Job, job_id)
    if not job:
        raise ApiError(404, "job_not_found", f"Job {job_id} was not found")
    return job


def submit_application(db: Session, job_id: int, data: ApplicationCreate) -> Application:
    job = get_job_or_404(db, job_id)
    email = str(data.email).lower()
    if job.is_closed:
        raise ApiError(409, "job_closed", "This job is closed and no longer accepts applications")
    if job.deadline < date.today():
        raise ApiError(409, "deadline_passed", "The application deadline has passed")
    if job.max_applicants is not None and application_count(db, job.id) >= job.max_applicants:
        raise ApiError(409, "applicant_cap_reached", "This job has reached its applicant limit")
    duplicate = db.scalar(
        select(Application.id).where(Application.job_id == job.id, Application.email == email)
    )
    if duplicate:
        raise ApiError(409, "duplicate_application", "This email has already applied to this job")

    payload = data.model_dump(mode="json")
    payload["email"] = email
    payload["linkedin_url"] = str(data.linkedin_url) if data.linkedin_url else None
    application = Application(job_id=job.id, status="pending", **payload)
    db.add(application)
    db.flush()
    db.add(
        StatusHistory(
            application_id=application.id,
            from_status=None,
            to_status="pending",
            note="Application submitted",
        )
    )
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ApiError(409, "duplicate_application", "This email has already applied to this job")
    return db.scalar(
        select(Application)
        .options(selectinload(Application.history))
        .where(Application.id == application.id)
    )


def update_status(db: Session, application_id: int, new_status: str, note: str) -> Application:
    application = db.scalar(
        select(Application)
        .options(selectinload(Application.history))
        .where(Application.id == application_id)
    )
    if not application:
        raise ApiError(404, "application_not_found", f"Application {application_id} was not found")
    if new_status not in ALLOWED_TRANSITIONS[application.status]:
        raise ApiError(
            409,
            "invalid_status_transition",
            f"Cannot move application from {application.status} to {new_status}",
            {"allowed_transitions": sorted(ALLOWED_TRANSITIONS[application.status])},
        )
    previous = application.status
    application.status = new_status
    db.add(
        StatusHistory(
            application_id=application.id,
            from_status=previous,
            to_status=new_status,
            note=note,
        )
    )
    db.commit()
    return db.scalar(
        select(Application)
        .options(selectinload(Application.history))
        .where(Application.id == application.id)
    )

