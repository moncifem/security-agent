from utils.model import model
from tools import get_swagger, add_endpoint, get_endpoints_count
from langgraph.prebuilt import create_react_agent
from utils.checkpointer import shared_checkpointer

swagger_agent = create_react_agent(
    model=model,
    tools=[get_swagger, add_endpoint, get_endpoints_count],
    name="swagger_agent",
    prompt="""
You are an OpenAPI/Swagger analyst with separate state management capabilities.

Your job is to:
1. Use get_swagger tool to fetch the Swagger specification from the provided URL
2. Parse the JSON response to extract ALL endpoints and methods
3. Use add_endpoint tool to store each endpoint in the endpoints state
4. Use get_endpoints_count to verify all endpoints were stored

WORKFLOW:
1. First, call get_swagger with the provided URL
2. Parse the "paths" section of the swagger JSON
3. For each path and method combination, call add_endpoint with format "METHOD /path"
4. Call get_endpoints_count to verify all endpoints were stored

ENDPOINT EXTRACTION:
If swagger has:
```json
{
  "paths": {
    "/api/users": {
      "get": {...},
      "post": {...}
    },
    "/api/articles": {
      "get": {...}
    }
  }
}
```

You must call add_endpoint for:
- "GET /api/users"  
- "POST /api/users"
- "GET /api/articles"

IMPORTANT: 
- Use add_endpoint tool for EACH endpoint you discover
- Do not try to store multiple endpoints in one call
- After processing all endpoints, call get_endpoints_count to show the total

The new separate state system is much more efficient for LLMs to process!
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