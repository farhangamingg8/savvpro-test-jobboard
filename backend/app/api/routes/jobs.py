from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import String, func, or_, select
from sqlalchemy.orm import Session, selectinload

from ...core.database import get_db
from ...core.errors import ApiError
from ...models.entities import Application, Job
from ...schemas.contracts import (
    ApplicationCreate,
    ApplicationRead,
    ApplicationStatus,
    JobCreate,
    JobListResponse,
    JobRead,
)
from ...services.hiring import create_job, get_job_or_404, job_payload, submit_application


router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("", response_model=JobRead, status_code=status.HTTP_201_CREATED)
def post_job(data: JobCreate, db: Session = Depends(get_db)):
    return job_payload(db, create_job(db, data))


@router.get("", response_model=JobListResponse)
def list_jobs(
    search: str | None = None,
    department: str | None = None,
    location: str | None = Query(default=None, pattern="^(remote|hybrid|onsite)$"),
    skill: str | None = None,
    include_closed: bool = False,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    filters = []
    if not include_closed:
        filters.extend((Job.is_closed.is_(False), Job.deadline >= date.today()))
    if search and search.strip():
        keyword = search.strip().lower()
        filters.append(
            or_(
                func.lower(Job.title).contains(keyword, autoescape=True),
                func.lower(Job.department).contains(keyword, autoescape=True),
            )
        )
    if department:
        filters.append(
            func.lower(Job.department).contains(department.strip().lower(), autoescape=True)
        )
    if location:
        filters.append(Job.location == location)
    if skill:
        # JSON is stored as text in SQLite; delimiters keep this an exact skill match.
        needle = f'%"{skill.strip().lower()}"%'
        filters.append(func.lower(func.cast(Job.required_skills, String)).like(needle))

    total = db.scalar(select(func.count(Job.id)).where(*filters)) or 0
    jobs = db.scalars(
        select(Job)
        .where(*filters)
        .order_by(Job.created_at.desc(), Job.id.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    ).all()
    return {"total_count": total, "page": page, "per_page": per_page, "results": [job_payload(db, j) for j in jobs]}


@router.get("/{job_id}", response_model=JobRead)
def get_job(job_id: int, db: Session = Depends(get_db)):
    return job_payload(db, get_job_or_404(db, job_id))


@router.post("/{job_id}/applications", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
def apply(job_id: int, data: ApplicationCreate, db: Session = Depends(get_db)):
    return submit_application(db, job_id, data)


@router.get("/{job_id}/applications", response_model=list[ApplicationRead])
def list_applications(
    job_id: int,
    status_filter: ApplicationStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    get_job_or_404(db, job_id)
    query = (
        select(Application)
        .options(selectinload(Application.history))
        .where(Application.job_id == job_id)
        .order_by(Application.created_at.desc())
    )
    if status_filter:
        query = query.where(Application.status == status_filter.value)
    return db.scalars(query).all()


@router.post("/{job_id}/close", response_model=JobRead)
def close_job(job_id: int, db: Session = Depends(get_db)):
    job = get_job_or_404(db, job_id)
    if job.is_closed:
        raise ApiError(409, "job_already_closed", "This job is already closed")
    job.is_closed = True
    db.commit()
    db.refresh(job)
    return job_payload(db, job)

