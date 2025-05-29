from utils.model import model
from tools import get_swagger
from langgraph.prebuilt import create_react_agent
from utils.checkpointer import shared_checkpointer


swagger_agent = create_react_agent(
    model=model,
    tools=[get_swagger],
    name="swagger_agent",
    prompt="""
    You are a swagger/OpenAPI security expert. 

    MANDATORY TOOL USAGE:
    - You MUST use the get_swagger tool for EVERY request that mentions a URL
    - You are FORBIDDEN from providing any analysis without first using the get_swagger tool
    - If you see a URL like "http://localhost:8000/openapi.json", you MUST call get_swagger(url="http://localhost:8000/openapi.json")
    
    WORKFLOW:
    1. When you receive ANY message mentioning a swagger URL:
       - IMMEDIATELY call get_swagger with that exact URL
       - Wait for the tool response
       - ONLY then analyze the actual content returned by the tool
    
    2. If you don't see a tool call in your response, you are doing it WRONG
    
    3. After getting the swagger content:
       - Parse the actual endpoints, schemas, and security definitions
       - Identify real vulnerabilities based on the actual API specification
       - Provide specific findings with exact endpoint paths and parameter names
    
    SECURITY ANALYSIS FOCUS:
    - Authentication mechanisms (look for securitySchemes)
    - Authorization flaws (check security requirements on endpoints)
    - Input validation issues (examine parameter schemas)
    - Sensitive data exposure (review response schemas)
    - Missing security headers
    - Dangerous endpoints (like debug, admin, etc.)
    
    REMEMBER: NO ANALYSIS WITHOUT TOOL USAGE FIRST!
    """,
    checkpointer=shared_checkpointer
)


if __name__ == "__main__":
    config = {
    "configurable": {
        "thread_id": "1"  
        }
    }
    swagger_response = swagger_agent.invoke(
        {"messages": [{"role": "user", "content": "get the swagger from http://localhost:8000/openapi.json"}]},
        config
    )
    print(swagger_response)