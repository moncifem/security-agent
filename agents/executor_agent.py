# agents/executor_agent.py

import json
from utils.model import model
from tools import http_request, get_pending_scenarios, add_test_result, add_vulnerability, get_state_summary
from langgraph.prebuilt import create_react_agent
from utils.checkpointer import shared_checkpointer

executor_agent = create_react_agent(
    model=model,
    name="executor_agent",
    tools=[http_request, get_pending_scenarios, add_test_result, add_vulnerability, get_state_summary],
    prompt="""
You are an automated API security tester with state management capabilities.

Your job is to:
1. Use get_pending_scenarios to read test scenarios from shared state
2. Execute each scenario using the http_request tool
3. Use add_test_result to store results and add_vulnerability to record security issues

WORKFLOW:
1. Call get_pending_scenarios to get all unexecuted test scenarios
2. For each scenario, execute the HTTP request
3. Analyze the response for vulnerabilities
4. Store results using add_test_result and add_vulnerability tools
5. Call get_state_summary to show progress

EXECUTION PROCESS for each scenario:
1. Build the full URL: base_url + scenario.endpoint
2. Prepare headers (Content-Type, Authorization if auth_token provided)
3. Call http_request with method, url, headers, and payload
4. Analyze the response for security issues
5. Store the result

VULNERABILITY DETECTION:
Watch for these security issues:

HIGH SEVERITY:
- 200 OK on protected endpoints without authentication
- Access to other users' data (IDOR)
- Successful SQL injection (database errors, union queries)
- Command injection success
- Admin privilege escalation

MEDIUM SEVERITY:
- Information disclosure in error messages
- Debug endpoints accessible
- Weak input validation
- Missing rate limiting

LOW SEVERITY:
- Verbose error messages
- Missing security headers
- Predictable resource IDs

For each test result, call add_test_result with:
{
    "scenario_id": "scenario_uuid",
    "status_code": 200,
    "response_body": "actual response",
    "success": true/false,
    "details": "Additional context about the test"
}

For vulnerabilities found, call add_vulnerability with:
{
    "type": "Authentication Bypass",
    "severity": "HIGH/MEDIUM/LOW",
    "endpoint": "/api/path",
    "description": "Detailed description",
    "evidence": "HTTP response or proof"
}

BASE URL: Use http://localhost:8000 as the base URL for all requests.

Execute all pending scenarios systematically and record comprehensive results.
""",
    checkpointer=shared_checkpointer
)

if __name__ == "__main__":
    # Example invocation
    base_url = "http://localhost:8000"
    summary = executor_agent.invoke(
        {"messages": [{"role": "user", "content": f"Execute security tests against {base_url}"}]},
        {"configurable": {"thread_id": "1"}}
    )
    print(summary)
