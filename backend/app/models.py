# backend/app/models.py
from pydantic import BaseModel
from typing import List, Optional

class ScrapeRequest(BaseModel):
    job_title: str
    location: str = "Remote"
    pages: int = 1

class JobData(BaseModel):
    Title: str
    Company: str
    Location: str
    Link: str

class ScrapeResponse(BaseModel):
    success: bool
    message: str
    jobs: List[JobData]
    total_jobs: int
    pages_scraped: int