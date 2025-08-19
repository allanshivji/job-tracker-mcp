import asyncio
import json
from typing import Any, Sequence
from datetime import date, datetime, timedelta

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
  Resource, 
  Tool, 
  TextContent, 
  ImageContent, 
  EmbeddedResource, 
  LoggingLevel
)
import mcp.types as types

from .database import db
from .models import JobApplicationCreate, ResumeVersionCreate, JobApplication

# Create the MCP server
server = Server("job-tracker-mcp")

def parse_date(date_str: str) -> date:
  """Parse date from various formats"""
  if date_str.lower() == "today":
    return date.today()
  elif date_str.lower() == "yesterday":
    return date.today() - timedelta(days=1)
  else:
    try:
      return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
      try:
        return datetime.strptime(date_str, "%m/%d/%Y").date()
      except ValueError:
        return date.today()  # fallback to today

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
  """List available MCP tools"""
  return [
      Tool(
          name="add_job_application",
          description="Add a new job application to track",
          inputSchema={
              "type": "object",
              "properties": {
                  "job_title": {"type": "string", "description": "Job title/position"},
                  "company_name": {"type": "string", "description": "Company name"},
                  "application_date": {"type": "string", "description": "Date applied (YYYY-MM-DD, today, yesterday)"},
                  "status": {"type": "string", "description": "Application status", "default": "applied"},
                  "job_url": {"type": "string", "description": "URL to job posting"},
                  "salary_range": {"type": "string", "description": "Salary range if known"},
                  "location": {"type": "string", "description": "Job location"},
                  "job_source": {"type": "string", "description": "Where you found the job (LinkedIn, Indeed, etc.)"},
                  "recruiter_name": {"type": "string", "description": "Recruiter contact name"},
                  "recruiter_email": {"type": "string", "description": "Recruiter email"},
                  "notes": {"type": "string", "description": "Additional notes"},
                  "resume_version": {"type": "string", "description": "Resume version used (defaults to 'default')"}
              },
              "required": ["job_title", "company_name"]
          }
      ),
      Tool(
          name="get_applications",
          description="Get job applications, optionally filtered by status, company, or job title",
          inputSchema={
              "type": "object",
              "properties": {
                  "status": {"type": "string", "description": "Filter by status (applied, interviewing, rejected, etc.)"},
                  "company_name": {"type": "string", "description": "Filter by company name"},
                  "job_title": {"type": "string", "description": "Filter by job title"},
                  "limit": {"type": "integer", "description": "Maximum number of results", "default": 10}
              }
          }
      ),
      Tool(
          name="update_application_status",
          description="Update the status of a job application",
          inputSchema={
              "type": "object",
              "properties": {
                  "application_id": {"type": "integer", "description": "Application ID"},
                  "new_status": {"type": "string", "description": "New status"},
                  "notes": {"type": "string", "description": "Additional notes about the update"}
              },
              "required": ["application_id", "new_status"]
          }
      ),
      Tool(
          name="add_resume_version",
          description="Add a new resume version",
          inputSchema={
              "type": "object",
              "properties": {
                  "name": {"type": "string", "description": "Resume version name"},
                  "content": {"type": "string", "description": "Resume text content"},
                  "description": {"type": "string", "description": "Description of this resume version"},
                  "is_default": {"type": "boolean", "description": "Set as default resume", "default": False}
              },
              "required": ["name", "content"]
          }
      ),
      Tool(
          name="list_resumes",
          description="List all resume versions",
          inputSchema={"type": "object", "properties": {}}
      ),
      Tool(
          name="get_application_stats",
          description="Get statistics about job applications",
          inputSchema={"type": "object", "properties": {}}
      )
  ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    """Handle tool calls from Claude"""
    
    if arguments is None:
        arguments = {}
    
    try:
        if name == "add_job_application":
            # Parse and validate data
            app_date = parse_date(arguments.get("application_date", "today"))
            
            app_data = JobApplicationCreate(
                job_title=arguments["job_title"],
                company_name=arguments["company_name"],
                application_date=app_date,
                status=arguments.get("status", "applied"),
                job_url=arguments.get("job_url"),
                salary_range=arguments.get("salary_range"),
                location=arguments.get("location"),
                job_source=arguments.get("job_source"),
                recruiter_name=arguments.get("recruiter_name"),
                recruiter_email=arguments.get("recruiter_email"),
                notes=arguments.get("notes"),
                resume_version_name=arguments.get("resume_version", "default")
            )
            
            application = db.add_job_application(app_data)
            
            # Get full application with resume info
            full_app = db.get_application_with_resume(application.id)
            resume_used = full_app.resume_version.name if full_app and full_app.resume_version else "None"
            
            return [types.TextContent(
                type="text",
                text=f"✅ Added job application:\n"
                     f"• Job: {application.job_title}\n"
                     f"• Company: {application.company_name}\n"
                     f"• Date: {application.application_date}\n"
                     f"• Status: {application.status}\n"
                     f"• Resume: {resume_used}\n"
                     f"• Application ID: {application.id}"
            )]
            
        elif name == "get_applications":
            # Get applications based on filters
            status = arguments.get("status")
            company_name = arguments.get("company_name")
            job_title = arguments.get("job_title")
            limit = arguments.get("limit", 10)
            
            if status:
                applications = db.get_applications_by_status(status)
            elif company_name or job_title:
                applications = db.search_applications(company_name, job_title)
            else:
                applications = db.get_all_applications_with_resumes()
            
            # Limit results
            applications = applications[:limit]
            
            if not applications:
                return [types.TextContent(type="text", text="No applications found matching your criteria.")]
            
            result = f"Found {len(applications)} application(s):\n\n"
            for app in applications:
                resume_name = "Unknown"
                try:
                    if hasattr(app, 'resume_version') and app.resume_version:
                        resume_name = app.resume_version.name
                except:
                    # Handle session issues
                    full_app = db.get_application_with_resume(app.id)
                    if full_app and full_app.resume_version:
                        resume_name = full_app.resume_version.name
                
                result += f"• **{app.job_title}** at **{app.company_name}**\n"
                result += f"  Applied: {app.application_date} | Status: {app.status} | Resume: {resume_name}\n"
                if app.salary_range:
                    result += f"  Salary: {app.salary_range}\n"
                if app.notes:
                    result += f"  Notes: {app.notes}\n"
                result += f"  ID: {app.id}\n\n"
            
            return [types.TextContent(type="text", text=result)]
            
        elif name == "update_application_status":
          app_id = arguments["application_id"]
          new_status = arguments["new_status"]
          notes = arguments.get("notes", "")
          
          # Get the application
          session = db.get_session()
          try:
            application = session.query(JobApplication).filter(JobApplication.id == app_id).first()  # Remove db. prefix
            if not application:
              return [types.TextContent(type="text", text=f"❌ Application with ID {app_id} not found.")]
            
            old_status = application.status
            application.status = new_status
            
            if notes:
              if application.notes:
                application.notes += f"\n[{datetime.now().strftime('%Y-%m-%d')}] {notes}"
              else:
                application.notes = f"[{datetime.now().strftime('%Y-%m-%d')}] {notes}"
            
            session.commit()
            
            return [types.TextContent(
              type="text",
              text=f"✅ Updated application status:\n"
                f"• Job: {application.job_title} at {application.company_name}\n"
                f"• Status: {old_status} → {new_status}\n"
                f"• Application ID: {app_id}"
            )]
          finally:
            session.close()
                
        elif name == "add_resume_version":
            resume_data = ResumeVersionCreate(
              name=arguments["name"],
              content=arguments["content"],
              description=arguments.get("description"),
              is_default=arguments.get("is_default", False)
            )
            
            resume = db.add_resume_version(resume_data)
            
            return [types.TextContent(
                type="text",
                text=f"✅ Added resume version:\n"
                     f"• Name: {resume.name}\n"
                     f"• Default: {resume.is_default}\n"
                     f"• Description: {resume.description or 'None'}\n"
                     f"• Resume ID: {resume.id}"
            )]
            
        elif name == "list_resumes":
            resumes = db.list_resumes()
            
            if not resumes:
                return [types.TextContent(type="text", text="No resume versions found.")]
            
            result = f"Found {len(resumes)} resume version(s):\n\n"
            for resume in resumes:
                default_marker = " ⭐ (DEFAULT)" if resume.is_default else ""
                result += f"• **{resume.name}**{default_marker}\n"
                if resume.description:
                    result += f"  Description: {resume.description}\n"
                result += f"  Created: {resume.created_at.strftime('%Y-%m-%d')}\n"
                result += f"  ID: {resume.id}\n\n"
            
            return [types.TextContent(type="text", text=result)]
            
        elif name == "get_application_stats":
            all_applications = db.get_all_applications_with_resumes()
            
            if not all_applications:
                return [types.TextContent(type="text", text="No applications found.")]
            
            # Calculate stats
            total = len(all_applications)
            status_counts = {}
            company_counts = {}
            
            for app in all_applications:
                status_counts[app.status] = status_counts.get(app.status, 0) + 1
                company_counts[app.company_name] = company_counts.get(app.company_name, 0) + 1
            
            result = f"📊 **Job Application Statistics**\n\n"
            result += f"**Total Applications:** {total}\n\n"
            
            result += "**By Status:**\n"
            for status, count in sorted(status_counts.items()):
                result += f"• {status}: {count}\n"
            
            result += "\n**Top Companies:**\n"
            sorted_companies = sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            for company, count in sorted_companies:
                result += f"• {company}: {count}\n"
            
            return [types.TextContent(type="text", text=result)]
        
        else:
            return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
            
    except Exception as e:
        return [types.TextContent(type="text", text=f"❌ Error: {str(e)}")]

async def main():
    """Run the MCP server"""
    # Initialize database
    db.create_tables()
    
    # Ensure default resume exists
    default_resume = db.get_default_resume()
    if not default_resume:
        db.add_resume_with_content(
            name="default",
            content="Please update this with your actual resume content.",
            description="Default resume - needs content",
            is_default=True
        )
        print("Created default resume placeholder")
    
    # Run the server
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, 
            write_stream, 
            InitializationOptions(
                server_name="job-tracker-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())