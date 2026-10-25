from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl, field_validator, model_validator


class Location(str, Enum):
    remote = "remote"
    hybrid = "hybrid"
    onsite = "onsite"


class ApplicationStatus(str, Enum):
    pending = "pending"
    shortlisted = "shortlisted"
    offered = "offered"
    rejected = "rejected"


class JobCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    department: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1)
    location: Location
    salary_min: int = Field(ge=0)
    salary_max: int = Field(gt=0)
    required_skills: list[str] = Field(min_length=1)
    max_applicants: int | None = Field(default=None, gt=0)
    deadline: date

    @field_validator("title", "department", "description")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

    @field_validator("required_skills")
    @classmethod
    def clean_skills(cls, value: list[str]) -> list[str]:
        cleaned = list(dict.fromkeys(skill.strip() for skill in value if skill.strip()))
        if not cleaned:
            raise ValueError("at least one non-blank skill is required")
        return cleaned

    @model_validator(mode="after")
    def salary_range_is_valid(self):
        if self.salary_min >= self.salary_max:
            raise ValueError("salary_min must be strictly less than salary_max")
        return self


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    department: str
    description: str
    location: Location
    salary_min: int
    salary_max: int
    required_skills: list[str]
    max_applicants: int | None
    deadline: date
    is_closed: bool
    created_at: datetime
    application_count: int = 0
    accepting_applications: bool = True


class JobListResponse(BaseModel):
    total_count: int
    page: int
    per_page: int
    results: list[JobRead]


class ApplicationCreate(BaseModel):
    applicant_name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    years_experience: int = Field(ge=0)
    cv_summary: str = Field(min_length=1, max_length=1000)
    linkedin_url: HttpUrl | None = None

    @field_validator("applicant_name", "cv_summary")
    @classmethod
    def strip_application_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

    @field_validator("linkedin_url")
    @classmethod
    def linkedin_only(cls, value: HttpUrl | None):
        if value is not None:
            url = str(value)
            allowed = ("https://linkedin.com/", "https://www.linkedin.com/")
            if not url.startswith(allowed):
                raise ValueError("must begin with https://linkedin.com/ or https://www.linkedin.com/")
        return value


class StatusHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    from_status: ApplicationStatus | None
    to_status: ApplicationStatus
    note: str
    created_at: datetime


class ApplicationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    applicant_name: str
    email: str
    years_experience: int
    cv_summary: str
    linkedin_url: str | None
    status: ApplicationStatus
    created_at: datetime
    history: list[StatusHistoryRead] = []


class StatusUpdate(BaseModel):
    status: ApplicationStatus
    note: str = Field(min_length=1, max_length=2000)

    @field_validator("note")
    @classmethod
    def note_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("a non-blank manager note is required")
        return value


class StatsRead(BaseModel):
    total_jobs: int
    open_jobs: int
    closed_jobs: int
    total_applications: int
    avg_applications_per_job: float
    top_department: str | None

