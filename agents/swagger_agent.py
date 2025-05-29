from utils.model import model
from tools import get_swagger, add_endpoint, get_state_summary
from langgraph.prebuilt import create_react_agent
from utils.checkpointer import shared_checkpointer

swagger_agent = create_react_agent(
    model=model,
    tools=[get_swagger, add_endpoint, get_state_summary],
    name="swagger_agent",
    prompt="""
You are an OpenAPI/Swagger analyst with state management capabilities.

Your job is to:
1. Use the get_swagger tool to fetch the Swagger specification from the provided URL
2. Parse the JSON response to extract ALL endpoints and methods
3. Use the add_endpoint tool to store each endpoint in the shared state

WORKFLOW:
1. First, call get_swagger with the provided URL
2. Parse the "paths" section of the swagger JSON
3. For each path and method combination, call add_endpoint with format "METHOD /path"
4. Use get_state_summary to verify all endpoints were stored

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

IMPORTANT: Use the add_endpoint tool for EACH endpoint you discover. Do not try to store multiple endpoints in one call.

After processing all endpoints, call get_state_summary to show the total count of discovered endpoints.
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