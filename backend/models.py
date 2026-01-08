from typing import List, Optional
from pydantic import BaseModel

class JobDescription(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    description: str
    keywords: List[str] = []

class Experience(BaseModel):
    title: str
    company: str
    start_date: str
    end_date: Optional[str] = None
    description: str

class Education(BaseModel):
    degree: str
    major: str
    university: str
    graduation_date: str

class Resume(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None # Added location field
    linkedin: Optional[str] = None
    github: Optional[str] = None
    summary: str
    skills: List[str] = []
    experience: List[Experience] = []
    education: List[Education] = []
    projects: List[str] = []
    certifications: List[str] = [] # Added certifications field

