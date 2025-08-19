from src.database import db
from src.models import ResumeVersionCreate, JobApplicationCreate
from datetime import date

def test_database_schema():
    try:
        # Create tables
        print("Creating database tables...")
        db.create_tables()
        
        # Check if default resume already exists
        print("Checking for existing default resume...")
        existing_resume = db.get_resume_by_name("default")
        
        if existing_resume:
            print(f"✅ Default resume already exists: {existing_resume.name} (ID: {existing_resume.id})")
            resume = existing_resume
        else:
            # Test adding a default resume
            print("Adding default resume...")
            default_resume = ResumeVersionCreate(
                name="default",
                file_path="resumes/default_resume.txt",
                description="My standard resume",
                is_default=True
            )
            resume = db.add_resume_version(default_resume)
            print(f"✅ Default resume added: {resume.name} (ID: {resume.id})")
        
        # Test adding a job application
        print("Adding test job application...")
        app_data = JobApplicationCreate(
            job_title="Senior Python Developer",
            company_name="TechCorp Inc",
            application_date=date.today(),
            status="applied",
            job_source="LinkedIn",
            notes="Looks like a great opportunity"
        )
        application = db.add_job_application(app_data)
        print(f"✅ Job application added: {application.job_title} at {application.company_name}")
        
        # Get the application with resume loaded properly
        print("Loading application with resume details...")
        full_application = db.get_application_with_resume(application.id)
        if full_application and full_application.resume_version:
            print(f"   Resume used: {full_application.resume_version.name}")
        else:
            print("   Resume used: None")
        
        # Test searching
        print("Testing search...")
        results = db.search_applications(company_name="TechCorp")
        print(f"✅ Found {len(results)} applications for TechCorp")
        
        # List all resumes
        print("Listing all resumes...")
        all_resumes = db.list_resumes()
        for r in all_resumes:
            default_marker = " (DEFAULT)" if r.is_default else ""
            print(f"  - {r.name}: {r.file_path or 'text content'}{default_marker}")
        
        # Test getting all applications with resumes
        print("Getting all applications with resume info...")
        all_apps = db.get_all_applications_with_resumes()
        for app in all_apps:
            resume_name = app.resume_version.name if app.resume_version else "None"
            print(f"  - {app.job_title} at {app.company_name} (Resume: {resume_name})")
        
        print("\n🎉 All database tests passed!")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database_schema()