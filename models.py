from pydantic import BaseModel,Field
from typing import List, Optional

class KeyDetails(BaseModel):
    job_function: str = Field(..., alias="Job Function")
    Industry: str
    Specialization: str
    Qualification: str

class DetailedInfo(BaseModel):
    job_description: str
    key_details: KeyDetails
    skills: List[str]
    job_posted_by: Optional[str] = None

class JobDetails(BaseModel):
    job_title: str
    company: str
    summary: str
    location: str
    experience: str
    salary: Optional[str] = None
    link: str
    detailed_info: DetailedInfo