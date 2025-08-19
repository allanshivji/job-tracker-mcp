from src.database import db

def setup_default_resume():
    """Set up your default resume"""
    
    # Your resume content as text
    default_resume_content = """
John Doe
Software Engineer
Email: john@email.com
Phone: (555) 123-4567

EXPERIENCE:
- Senior Developer at TechCorp (2022-Present)
  * Built scalable web applications
  * Led team of 5 developers
  
- Developer at StartupXYZ (2020-2022)
  * Full-stack development
  * Microservices architecture

SKILLS:
- Python, JavaScript, SQL
- Django, React, PostgreSQL
- AWS, Docker, Kubernetes

EDUCATION:
- BS Computer Science, University (2020)
"""
    
    try:
        # Create tables first
        db.create_tables()
        
        # Check if default resume exists
        existing = db.get_resume_by_name("default")
        if existing:
            print("✅ Default resume already exists")
            return existing
        
        # Add default resume
        resume = db.add_resume_with_content(
            name="default",
            content=default_resume_content.strip(),
            description="My standard software engineer resume",
            is_default=True
        )
        
        print(f"✅ Default resume created: {resume.name} (ID: {resume.id})")
        return resume
        
    except Exception as e:
        print(f"❌ Error setting up resume: {e}")
        return None

if __name__ == "__main__":
    setup_default_resume()