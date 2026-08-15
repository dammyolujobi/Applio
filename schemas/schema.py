from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class JobType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    REMOTE = "remote"

class ExperienceLevel(str, Enum):
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    EXECUTIVE = "executive"

class User(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[List[str]] = []

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class JobFilter(BaseModel):
    role: str
    location: Optional[str] = None
    job_type: Optional[JobType] = None
    experience_level: Optional[ExperienceLevel] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    company: Optional[str] = None

class JobSort(BaseModel):
    field: str = "date"  # date, salary, relevance
    order: str = "desc"  # asc or desc

class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20

class JobListing(BaseModel):
    title: str
    company: str
    description: Optional[str] = None
    date: Optional[str] = None
    job_url: str
    company_url: Optional[str] = None
    location: Optional[str] = None
    salary: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    source: Optional[str] = None
    job_id: Optional[str] = None

class JobDetail(JobListing):
    requirements: Optional[List[str]] = []
    benefits: Optional[List[str]] = []
    application_deadline: Optional[str] = None
    remote_option: Optional[bool] = False

class SavedJob(BaseModel):
    job_id: str
    user_email: str
    saved_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None

class JobAlert(BaseModel):
    user_email: str
    role_keywords: List[str]
    location: Optional[str] = None
    job_type: Optional[JobType] = None
    min_salary: Optional[int] = None
    frequency: str = "daily"  # daily, weekly
    is_active: bool = True

class Application(BaseModel):
    job_id: str
    user_email: str
    company: str
    position: str
    status: str = "applied"  # applied, interviewing, offered, rejected, withdrawn
    applied_date: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = None
    job_url: Optional[str] = None

class SearchHistory(BaseModel):
    user_email: str
    query: str
    location: Optional[str] = None
    filters: Optional[dict] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class UserActivity(BaseModel):
    user_email: str
    action: str  # login, search, view_job, save_job, apply
    details: Optional[dict] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1440

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class AggregatedJobsResponse(BaseModel):
    jobs: List[JobListing]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
    filters_applied: dict

class AdminDashboardStats(BaseModel):
    total_users: int
    total_jobs_scraped: int
    active_alerts: int
    total_applications: int
    searches_last_24h: int
    top_searches: List[dict]
    user_growth: List[dict]