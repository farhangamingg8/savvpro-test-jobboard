from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    department: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[str] = mapped_column(Text)
    location: Mapped[str] = mapped_column(String(20), index=True)
    salary_min: Mapped[int] = mapped_column(Integer)
    salary_max: Mapped[int] = mapped_column(Integer)
    required_skills: Mapped[list[str]] = mapped_column(JSON)
    max_applicants: Mapped[int | None] = mapped_column(Integer, nullable=True)
    deadline: Mapped[date] = mapped_column(Date, index=True)
    is_closed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    applications: Mapped[list["Application"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (UniqueConstraint("job_id", "email", name="uq_application_job_email"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), index=True)
    applicant_name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(320))
    years_experience: Mapped[int] = mapped_column(Integer)
    cv_summary: Mapped[str] = mapped_column(Text)
    linkedin_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    job: Mapped[Job] = relationship(back_populates="applications")
    history: Mapped[list["StatusHistory"]] = relationship(
        back_populates="application",
        cascade="all, delete-orphan",
        order_by="StatusHistory.created_at",
    )


class StatusHistory(Base):
    __tablename__ = "status_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"), index=True)
    from_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    to_status: Mapped[str] = mapped_column(String(20))
    note: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    application: Mapped[Application] = relationship(back_populates="history")

