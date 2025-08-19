from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel

Base = declarative_base()

# SQLAlchemy Models (Database Tables)
class ResumeVersion(Base):
  __tablename__ = "resume_versions"
    
  id = Column(Integer, primary_key=True)
  name = Column(String(100), nullable=False, unique=True)
  file_path = Column(String(500), nullable=True)  # Made nullable
  content = Column(Text, nullable=True)  # Add this line for text content
  description = Column(Text)
  is_default = Column(Boolean, default=False)
  created_at = Column(DateTime, default=datetime.utcnow)
  
  # Relationship to applications
  applications = relationship("JobApplication", back_populates="resume_version")

class JobApplication(Base):
  __tablename__ = "job_applications"
  
  id = Column(Integer, primary_key=True)
  job_title = Column(String(200), nullable=False)
  company_name = Column(String(200), nullable=False)
  application_date = Column(Date, nullable=False)
  status = Column(String(50), default="applied")
  job_url = Column(Text)
  salary_range = Column(String(100))
  location = Column(String(200))
  job_source = Column(String(100))  # LinkedIn, Indeed, Company Website, etc.
  
  # Contact information
  recruiter_name = Column(String(200))
  recruiter_email = Column(String(200))
  
  # Follow-up tracking
  next_followup_date = Column(Date)
  
  # Notes and details
  notes = Column(Text)
  
  # Resume version used
  resume_version_id = Column(Integer, ForeignKey("resume_versions.id"))
  resume_version = relationship("ResumeVersion", back_populates="applications")
  
  # Timestamps
  created_at = Column(DateTime, default=datetime.utcnow)
  updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Pydantic Models (API/Data Validation)
class ResumeVersionCreate(BaseModel):
  name: str
  file_path: Optional[str] = None
  content: Optional[str] = None  # Add this line
  description: Optional[str] = None
  is_default: bool = False

class ResumeVersionResponse(BaseModel):
  id: int
  name: str
  file_path: Optional[str]
  content: Optional[str]  # Add this line
  description: Optional[str]
  is_default: bool
  created_at: datetime
  
  class Config:
      from_attributes = True

class JobApplicationCreate(BaseModel):
  job_title: str
  company_name: str
  application_date: date
  status: str = "applied"
  job_url: Optional[str] = None
  salary_range: Optional[str] = None
  location: Optional[str] = None
  job_source: Optional[str] = None
  recruiter_name: Optional[str] = None
  recruiter_email: Optional[str] = None
  next_followup_date: Optional[date] = None
  notes: Optional[str] = None
  resume_version_name: Optional[str] = None  # Will lookup by name

class JobApplicationResponse(BaseModel):
  id: int
  job_title: str
  company_name: str
  application_date: date
  status: str
  job_url: Optional[str]
  salary_range: Optional[str]
  location: Optional[str]
  job_source: Optional[str]
  recruiter_name: Optional[str]
  recruiter_email: Optional[str]
  next_followup_date: Optional[date]
  notes: Optional[str]
  resume_version: Optional[ResumeVersionResponse]
  created_at: datetime
  updated_at: datetime
  
  class Config:
    from_attributes = True