import asyncio
from src.server import handle_list_tools, handle_call_tool

async def test_server_tools():
    """Test the MCP server tools locally"""
    
    print("Testing MCP Server Tools\n" + "="*40)
    
    # Test 1: List tools
    print("1. Testing list_tools...")
    try:
        tools = await handle_list_tools()
        print(f"✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description}")
    except Exception as e:
        print(f"❌ Error listing tools: {e}")
    print()
    
    # Test 2: Add a job application
    print("2. Testing add_job_application...")
    try:
        result = await handle_call_tool(
            "add_job_application",
            {
                "job_title": "Python Developer",
                "company_name": "TestCorp",
                "application_date": "today",
                "status": "applied",
                "job_source": "LinkedIn",
                "notes": "This is a test application"
            }
        )
        print("✅ Add application result:")
        print(result[0].text)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    print()
    
    # Test 3: Get applications
    print("3. Testing get_applications...")
    try:
        result = await handle_call_tool("get_applications", {"limit": 5})
        print("✅ Get applications result:")
        print(result[0].text)
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Test 4: List resumes
    print("4. Testing list_resumes...")
    try:
        result = await handle_call_tool("list_resumes", {})
        print("✅ List resumes result:")
        print(result[0].text)
    except Exception as e:
        print(f"❌ Error: {e}")
    print()
    
    # Test 5: Get stats
    print("5. Testing get_application_stats...")
    try:
        result = await handle_call_tool("get_application_stats", {})
        print("✅ Stats result:")
        print(result[0].text)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎉 MCP Server testing complete!")

if __name__ == "__main__":
    asyncio.run(test_server_tools())