from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import os
from typing import List, Optional
from datetime import date, datetime
from sqlalchemy.orm import joinedload

from .models import Base, JobApplication, ResumeVersion, JobApplicationCreate, ResumeVersionCreate

load_dotenv()

class DatabaseManager:
  def __init__(self):
    self.database_url = os.getenv('DATABASE_URL')
    self.engine = create_engine(self.database_url)
    self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
  def create_tables(self):
    """Create all tables in the database"""
    Base.metadata.create_all(bind=self.engine)
    print("✅ Database tables created successfully!")
        
  def get_session(self) -> Session:
    """Get a database session"""
    return self.SessionLocal()
    
  # Resume Version Operations
  def add_resume_version(self, resume_data: ResumeVersionCreate) -> ResumeVersion:
    """Add a new resume version"""
    session = self.get_session()
    try:
      # If this is set as default, unset all other defaults
      if resume_data.is_default:
          session.query(ResumeVersion).update({"is_default": False})
      
      resume = ResumeVersion(**resume_data.dict())
      session.add(resume)
      session.commit()
      session.refresh(resume)
      return resume
    except SQLAlchemyError as e:
      session.rollback()
      raise e
    finally:
      session.close()

  def add_resume_with_content(self, name: str, content: str, description: str = None, is_default: bool = False) -> ResumeVersion:
    """Add a resume with text content"""
    resume_data = ResumeVersionCreate(
      name=name,
      content=content,
      description=description,
      is_default=is_default
    )
    return self.add_resume_version(resume_data)
    
  def get_default_resume(self) -> Optional[ResumeVersion]:
    """Get the default resume version"""
    session = self.get_session()
    try:
      return session.query(ResumeVersion).filter(ResumeVersion.is_default == True).first()
    finally:
      session.close()
    
  def get_or_create_default_resume(self) -> ResumeVersion:
    """Get default resume or create one if it doesn't exist"""
    default_resume = self.get_default_resume()
    if not default_resume:
      # Create a basic default resume
      default_resume = self.add_resume_with_content(
        name="default",
        content="This is a placeholder for your default resume content.",
        description="Default resume - please update with your actual resume content",
        is_default=True
      )
    return default_resume

  def get_resume_by_name(self, name: str) -> Optional[ResumeVersion]:
    """Get resume version by name"""
    session = self.get_session()
    try:
      return session.query(ResumeVersion).filter(ResumeVersion.name == name).first()
    finally:
      session.close()
    
  def list_resumes(self) -> List[ResumeVersion]:
    """Get all resume versions"""
    session = self.get_session()
    try:
        return session.query(ResumeVersion).order_by(ResumeVersion.created_at.desc()).all()
    finally:
        session.close()
    
  def add_job_application(self, app_data: JobApplicationCreate) -> JobApplication:
    """Add a new job application"""
    session = self.get_session()
    try:
      # Handle resume version
      resume_version = None
      if app_data.resume_version_name:
          resume_version = self.get_resume_by_name(app_data.resume_version_name)
      else:
          resume_version = self.get_default_resume()
      
      # Create application
      app_dict = app_data.dict()
      app_dict.pop('resume_version_name', None)  # Remove this field
      
      application = JobApplication(**app_dict)
      if resume_version:
          application.resume_version_id = resume_version.id
      
      session.add(application)
      session.commit()
      session.refresh(application)
      
      # Eagerly load the resume_version relationship before closing session
      if application.resume_version_id:
          _ = application.resume_version.name  # This loads the relationship
      
      return application
    except SQLAlchemyError as e:
      session.rollback()
      raise e
    finally:
        session.close()


  def get_application_with_resume(self, application_id: int) -> Optional[JobApplication]:
    """Get application with resume version eagerly loaded"""
    session = self.get_session()
    try:
      return session.query(JobApplication).options(
        joinedload(JobApplication.resume_version)
      ).filter(JobApplication.id == application_id).first()
    finally:
      session.close()

  def get_all_applications_with_resumes(self) -> List[JobApplication]:
    """Get all applications with resume versions eagerly loaded"""
    session = self.get_session()
    try:
      return session.query(JobApplication).options(
        joinedload(JobApplication.resume_version)
      ).order_by(JobApplication.application_date.desc()).all()
    finally:
      session.close()

  def get_applications_by_status(self, status: str) -> List[JobApplication]:
    """Get applications by status"""
    session = self.get_session()
    try:
      return session.query(JobApplication).filter(JobApplication.status == status).all()
    finally:
      session.close()
    
  def search_applications(self, company_name: str = None, job_title: str = None) -> List[JobApplication]:
    """Search applications by company or job title"""
    session = self.get_session()
    try:
      query = session.query(JobApplication)
      if company_name:
        query = query.filter(JobApplication.company_name.ilike(f"%{company_name}%"))
      if job_title:
        query = query.filter(JobApplication.job_title.ilike(f"%{job_title}%"))
      return query.order_by(JobApplication.application_date.desc()).all()
    finally:
      session.close()

# Global database instance
db = DatabaseManager()