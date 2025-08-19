# Job Tracker MCP Server

A Model Context Protocol (MCP) server for tracking job applications through natural conversation with Claude AI. Manage your job search, resumes, and application status updates seamlessly.

## Features

- **Job Application Tracking**: Add, update, and search job applications
- **Resume Management**: Store multiple resume versions with text content
- **Status Updates**: Track application progress from applied to hired
- **Natural Language Interface**: Interact through conversational commands with Claude
- **Statistics & Analytics**: Get insights on your job search progress
- **Database Storage**: Persistent PostgreSQL storage for all your data

## Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- Claude Desktop (for MCP integration)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/job-tracker-mcp.git
cd job-tracker-mcp
```

### 2. Set Up Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up PostgreSQL

Install PostgreSQL. The server will use the default `postgres` database:

```bash
# On macOS with Homebrew
brew install postgresql
brew services start postgresql

# On Ubuntu/Linux
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql

# On Windows - download installer from postgresql.org
```

### 5. Configure Environment

Add `.env`:
```env
DATABASE_URL=postgresql://postgres@localhost:5432/job_applications
```

### 6. Initialize Database

```bash
python3 test_schema.py
```

## Claude Desktop Configuration

### 1. Locate Claude's Configuration Directory

- **macOS**: `~/Library/Application Support/Claude/`
- **Windows**: `%APPDATA%\Claude\`
- **Linux**: `~/.config/Claude/`

### 2. Create or Edit MCP Configuration

Create or edit `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "job-tracker": {
      "command": "python3",
      "args": ["/full/path/to/your/project/run_server.py"],
      "env": {
        "PYTHONPATH": "/full/path/to/your/project"
      }
    }
  }
}
```

Replace `/full/path/to/your/project` with your actual project path.

### 3. Restart Claude Desktop

Completely quit and restart Claude Desktop to load the new MCP server.

## Usage Examples

### Adding Your First Resume

```
Add a resume version called "software-engineer" with this content:

John Doe
Senior Software Engineer
Email: john@example.com
Phone: (555) 123-4567

EXPERIENCE:
Senior Software Engineer at TechCorp (2022-Present)
• Led development of microservices architecture
• Managed team of 5 engineers

SKILLS:
• Python, JavaScript, SQL
• React, Django, PostgreSQL
• AWS, Docker, Kubernetes

Set this as my default resume.
```

### Adding Job Applications

```
Add a job application: Senior Python Developer at Google, applied today, found on LinkedIn, salary range $150k-200k
```

```
Add application: Data Scientist at Netflix, applied yesterday, $130k-160k, remote position
```

### Viewing Applications

```
Show me all my job applications
```

```
Show me applications with status "applied"
```

```
Find all applications at Google
```

### Updating Application Status

```
Update application ID 1 to status "interviewing" with note "Phone screen scheduled for Friday"
```

```
Mark application 3 as rejected - they said they went with an internal candidate
```

### Resume Management

```
Add a new resume version called "data-science-focused" with this content:
[paste your data science resume here]
```

```
Set my "data-science-focused" resume as the default
```

```
Show me the content of my "software-engineer" resume
```

```
List all my resume versions
```

### Statistics and Analytics

```
Show me my job application statistics
```

```
How many applications have I submitted this month?
```

## Available MCP Tools

The server provides these tools for Claude:

1. **add_job_application** - Add new job applications
2. **get_applications** - Retrieve and filter applications
3. **update_application_status** - Update application status
4. **add_resume_version** - Add new resume versions
5. **set_default_resume** - Set default resume
6. **get_resume_content** - View resume content
7. **list_resumes** - List all resume versions
8. **get_application_stats** - Get application statistics

## Development

### Running Tests

```bash
# Test database connection
python3 test_connection.py

# Test database schema
python3 test_schema.py

# Test MCP server tools
python3 test_mcp_server.py
```

## Troubleshooting

### MCP Server Not Recognized

1. Verify the path in `claude_desktop_config.json` is correct
2. Check that `run_server.py` is executable
3. Restart Claude Desktop completely
4. Check the log file: `/tmp/job_tracker_mcp.log`

### Database Connection Issues

1. Ensure PostgreSQL is running
2. Verify database credentials in `.env`
3. Test connection: `python3 test_connection.py`

### Server Startup Issues

1. Check Python version: `python3 --version`
2. Verify virtual environment is activated
3. Ensure all dependencies are installed: `pip install -r requirements.txt`