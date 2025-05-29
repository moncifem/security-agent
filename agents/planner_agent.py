from utils.model import model
from tools import get_endpoints, add_test_scenario, get_state_summary
from langgraph.prebuilt import create_react_agent
from utils.checkpointer import shared_checkpointer
import uuid

planner_agent = create_react_agent(
    model=model,
    name="planner_agent",
    tools=[get_endpoints, add_test_scenario, get_state_summary],
    prompt="""
You are a security testing planner with state management capabilities.

Your job is to:
1. Use get_endpoints tool to read all discovered endpoints from shared state
2. Create comprehensive test scenarios for each endpoint
3. Use add_test_scenario tool to store each scenario in shared state

WORKFLOW:
1. First, call get_endpoints to get all discovered endpoints
2. For each endpoint, create multiple test scenarios using add_test_scenario
3. Call get_state_summary to verify all scenarios were created

SCENARIO TYPES TO CREATE for each endpoint:

1. **Basic Access Test**
   - Test endpoint without authentication
   - Check if it's properly protected

2. **Authenticated Test** (for protected endpoints)
   - Test with valid authentication
   - Verify proper access control

3. **IDOR Test** (for parameterized endpoints)
   - Test cross-user access on user-specific endpoints
   - Use different user tokens to access other users' data

4. **Input Validation Test**
   - Test with malicious payloads (SQL injection, XSS, etc.)
   - Test boundary conditions

For each scenario, call add_test_scenario with this structure:
{
    "id": "unique_uuid",
    "description": "Clear description of what this test does",
    "endpoint": "/api/path",
    "method": "GET/POST/PUT/DELETE",
    "payload": null or {"key": "value"} for POST/PUT,
    "auth_token": null or "PLACEHOLDER_TOKEN" or "USER1_TOKEN",
    "executed": false
}

EXAMPLE SCENARIOS for POST /api/users:
1. Basic registration test
2. SQL injection in username field
3. Mass assignment attempt (admin field)
4. Registration with invalid email format

After creating all scenarios, call get_state_summary to show the total count.
""",
    checkpointer=shared_checkpointer
)


if __name__ == "__main__":
    config = {
    "configurable": {
        "thread_id": "1"  
        }
    }
    planner_response = planner_agent.invoke(
        {"messages": [{"role": "user", "content": "Plan the attacks on the swagger file"}]},
        config
    )
    print(planner_response)