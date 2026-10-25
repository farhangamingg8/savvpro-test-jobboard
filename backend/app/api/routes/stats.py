from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...models.entities import Application, Job
from ...schemas.contracts import StatsRead


router = APIRouter(prefix="/api/stats", tags=["analytics"])


@router.get("", response_model=StatsRead)
def get_stats(db: Session = Depends(get_db)):
    total_jobs = db.scalar(select(func.count(Job.id))) or 0
    open_jobs = db.scalar(
        select(func.count(Job.id)).where(Job.is_closed.is_(False), Job.deadline >= date.today())
    ) or 0
    total_applications = db.scalar(select(func.count(Application.id))) or 0
    top_department = db.execute(
        select(Job.department, func.count(Job.id).label("job_count"))
        .group_by(Job.department)
        .order_by(desc("job_count"), Job.department.asc())
        .limit(1)
    ).first()
    return {
        "total_jobs": total_jobs,
        "open_jobs": open_jobs,
        "closed_jobs": total_jobs - open_jobs,
        "total_applications": total_applications,
        "avg_applications_per_job": round(total_applications / total_jobs, 2) if total_jobs else 0.0,
        "top_department": top_department[0] if top_department else None,
    }

