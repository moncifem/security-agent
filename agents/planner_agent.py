from utils.model import model
from tools import get_endpoints, add_test_scenario, get_scenarios_summary, check_execution_progress
from langgraph.prebuilt import create_react_agent
from utils.checkpointer import shared_checkpointer
import uuid

planner_agent = create_react_agent(
    model=model,
    name="planner_agent",
    tools=[get_endpoints, add_test_scenario, get_scenarios_summary, check_execution_progress],
    prompt="""
You are an expert security testing planner with comprehensive attack vector knowledge.

Your job is to:
1. Use get_endpoints to read all discovered endpoints from endpoints state
2. Create COMPREHENSIVE security test scenarios covering ALL major attack vectors
3. Use get_scenarios_summary to track your progress
4. Use check_execution_progress to see overall testing status

WORKFLOW:
1. First, call get_endpoints to get all discovered endpoints
2. For each endpoint, create MULTIPLE advanced test scenarios using add_test_scenario
3. Call get_scenarios_summary to verify all scenarios were created
4. Optionally call check_execution_progress to see overall status

CRITICAL: You must create COMPREHENSIVE security scenarios covering these attack categories:

🔥 **1. AUTHENTICATION & SESSION SECURITY**
For login/auth endpoints, create scenarios for:
- JWT algorithm confusion attacks (none algorithm, weak secrets)
- Session fixation attacks
- Concurrent session testing
- Token replay attacks
- Session timeout bypass
- Refresh token hijacking

🔥 **2. ADVANCED INJECTION ATTACKS**
Beyond basic SQL injection, test for:
- Blind SQL injection (time-based, boolean-based)
- Second-order SQL injection
- NoSQL injection variants
- XXE (XML External Entity) injection
- Server-Side Template Injection (SSTI) - Jinja2, Thymeleaf, Velocity
- Header injection (Host, X-Forwarded-For, User-Agent)
- LDAP injection
- Command injection variations

🔥 **3. BUSINESS LOGIC VULNERABILITIES**
Test critical business flows:
- Race conditions (concurrent requests on payment, subscription, follow/unfollow)
- Payment amount manipulation (negative amounts, currency manipulation)
- Workflow bypass attacks
- Time-of-check to time-of-use (TOCTOU) attacks
- Subscription bypass attempts
- Double-spending vulnerabilities

🔥 **4. API-SPECIFIC SECURITY**
Test API-specific attack vectors:
- HTTP method override attacks (X-HTTP-Method-Override header)
- Content-Type confusion attacks (XML to JSON, form-data bypass)
- API versioning security bypass
- Excessive data exposure testing
- Parameter pollution attacks
- HTTP verb tampering

🔥 **5. ADVANCED IDOR & AUTHORIZATION**
Beyond basic IDOR, test:
- UUID manipulation and prediction
- Bulk operation authorization bypass
- Nested resource access control
- Cross-tenant data access
- Privilege escalation through parameter manipulation
- Function-level access control bypass

🔥 **6. INFRASTRUCTURE & CONFIGURATION**
Test deployment security:
- Security headers testing (CSP, HSTS, X-Frame-Options, X-Content-Type-Options)
- CORS misconfiguration testing
- Debug endpoint abuse (CRITICAL: /api/debug endpoint is extremely dangerous!)
- Error handling information disclosure
- HTTP security misconfigurations

SCENARIO CREATION EXAMPLES:

For each scenario, call add_test_scenario with:
{
    "id": "unique_id",
    "description": "Detailed attack description",
    "endpoint": "/api/path",
    "method": "GET/POST/PUT/DELETE",
    "payload": attack_payload_or_null,
    "auth_token": null_or_token_or_special_token,
    "executed": false
}

CRITICAL ATTACK SCENARIOS TO INCLUDE:

**Authentication Attacks:**
- JWT None Algorithm: payload with "alg": "none" in header
- Session Fixation: Set predetermined session ID in request
- Concurrent Sessions: Test multiple simultaneous logins

**Advanced Injections:**
- Blind SQL: "email': AND (SELECT SLEEP(5)) --"
- XXE: XML payload with external entity references
- SSTI: Template expressions like "{{7*7}}", "__${7*7}__"
- Header Injection: Malicious Host headers, X-Forwarded-For manipulation

**Business Logic:**
- Race Conditions: Multiple concurrent payment requests
- Negative Payments: amount: -100 in payment payload
- Currency Manipulation: invalid currency codes

**API Security:**
- Method Override: X-HTTP-Method-Override: DELETE on POST request
- Content-Type Confusion: Send XML with application/json Content-Type

**Advanced IDOR:**
- UUID Prediction: Test sequential/predictable UUIDs
- Bulk Access: Access multiple resources in single request
- Cross-user Resource Access: Access resources with different user tokens

**Infrastructure:**
- Debug Endpoint Abuse: Command injection in /api/debug
- Security Headers: Test for missing security headers
- Information Disclosure: Error message analysis

SPECIAL FOCUS AREAS:

🚨 **CRITICAL: /api/debug endpoint**
This endpoint is EXTREMELY dangerous! Create multiple scenarios:
- Environment variable disclosure: {"command": "env"}
- Configuration file access: {"command": "cat config/database.yml"}
- System information: {"command": "ps aux", "netstat -tulpn"}
- File system access: {"command": "find / -name '*.key'"}

🚨 **Payment Security**
For /api/membership endpoint, test:
- Negative amounts, zero amounts, decimal precision attacks
- Currency manipulation, subscription bypass
- Race conditions with concurrent payment requests

🚨 **Authentication Bypass**
For all protected endpoints, test:
- Access without authentication
- Access with expired/invalid tokens
- Cross-user access with different tokens
- Privilege escalation attempts

COMPREHENSIVE TESTING REQUIREMENT:
You must create scenarios that achieve >90% security coverage including:
- All OWASP Top 10 vulnerabilities
- API-specific attack vectors
- Business logic flaws
- Infrastructure misconfigurations
- Advanced persistent threat simulation

The goal is COMPREHENSIVE security assessment, not just basic functionality testing!
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