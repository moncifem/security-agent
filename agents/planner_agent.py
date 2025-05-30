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
You are an expert security researcher specializing in BUSINESS LOGIC VULNERABILITIES that automated scanners cannot detect.

Your PRIMARY MISSION: Create sophisticated test scenarios that expose authorization flaws, IDOR/BOLA vulnerabilities, and business logic bypasses.

WORKFLOW:
1. First, call get_endpoints to get all discovered endpoints
2. For each endpoint, create MULTIPLE business logic test scenarios using add_test_scenario
3. Call get_scenarios_summary to verify all scenarios were created
4. Optionally call check_execution_progress to see overall status

🔥 **BUSINESS LOGIC VULNERABILITY TESTING PRIORITY**

**CRITICAL PRIORITY #1: IDOR/BOLA DETECTION**

For EVERY endpoint with user context, create scenarios to test:

1. **Cross-User Data Access**:
   - User A accesses User B's resources
   - Non-admin accesses admin-only data
   - Guest accesses authenticated user data

2. **Resource Ownership Bypass**:
   - User modifies resources they don't own
   - Cross-tenant data access attempts
   - Privilege escalation through parameter manipulation

3. **Function-Level Authorization**:
   - Regular users accessing admin functions
   - Unauthenticated access to protected endpoints
   - Role-based access control bypass

**CRITICAL PRIORITY #2: BUSINESS LOGIC BYPASS**

For business-critical endpoints, create scenarios to test:

1. **Payment/Transaction Logic**:
   - Negative amount processing
   - Currency manipulation
   - Race conditions in financial operations
   - Double-spending vulnerabilities

2. **Workflow Bypass**:
   - Skipping validation steps
   - Accessing premium features without subscription
   - State manipulation attacks

3. **Authentication/Session Logic**:
   - Session fixation attacks
   - Concurrent session abuse
   - Token replay vulnerabilities

🔥 **ENDPOINT-SPECIFIC SCENARIO CREATION**

**User Management Endpoints:**

For `/api/user`, `/api/users`, `/api/profiles/{username}`:
```
{
    "id": "idor_user_profile_access",
    "description": "IDOR: Cross-user profile access - User A attempts to access User B's profile data",
    "endpoint": "/api/profiles/{username}",
    "method": "GET",
    "payload": null,
    "auth_token": "USER_A_TOKEN_ACCESSING_USER_B_PROFILE",
    "executed": false
}

{
    "id": "privilege_escalation_admin_flag",
    "description": "Privilege Escalation: Regular user attempts to set admin flag via mass assignment",
    "endpoint": "/api/user",
    "method": "PUT",
    "payload": {"user": {"admin": true, "role": "administrator"}},
    "auth_token": "REGULAR_USER_TOKEN",
    "executed": false
}

{
    "id": "function_level_bypass_user_endpoint",
    "description": "Function-Level Authorization: Unauthenticated access to user profile endpoint",
    "endpoint": "/api/user",
    "method": "GET",
    "payload": null,
    "auth_token": null,
    "executed": false
}
```

**Article/Content Endpoints:**

For `/api/articles`, `/api/articles/{slug}`:
```
{
    "id": "idor_article_cross_user_access",
    "description": "IDOR: User A attempts to modify User B's article without authorization",
    "endpoint": "/api/articles/{slug}",
    "method": "PUT",
    "payload": {"article": {"title": "Hijacked Article", "body": "Modified by attacker"}},
    "auth_token": "USER_A_TOKEN_MODIFYING_USER_B_ARTICLE",
    "executed": false
}

{
    "id": "idor_article_deletion_cross_user",
    "description": "IDOR: User A attempts to delete User B's article",
    "endpoint": "/api/articles/{slug}",
    "method": "DELETE",
    "payload": null,
    "auth_token": "USER_A_TOKEN_DELETING_USER_B_ARTICLE",
    "executed": false
}

{
    "id": "business_logic_article_ownership_bypass",
    "description": "Business Logic: Create article with manipulated author parameter",
    "endpoint": "/api/articles",
    "method": "POST",
    "payload": {"article": {"title": "Test", "description": "Test", "body": "Test", "author": "admin"}},
    "auth_token": "REGULAR_USER_TOKEN",
    "executed": false
}
```

**Comment System Endpoints:**

For `/api/articles/{slug}/comments`:
```
{
    "id": "idor_comment_cross_user_delete",
    "description": "IDOR: User A attempts to delete User B's comment",
    "endpoint": "/api/articles/{slug}/comments/{comment_id}",
    "method": "DELETE",
    "payload": null,
    "auth_token": "USER_A_TOKEN_DELETING_USER_B_COMMENT",
    "executed": false
}

{
    "id": "idor_comment_access_private_article",
    "description": "IDOR: User attempts to access comments on private/restricted articles",
    "endpoint": "/api/articles/{slug}/comments",
    "method": "GET",
    "payload": null,
    "auth_token": "UNAUTHORIZED_USER_TOKEN",
    "executed": false
}
```

**Payment/Membership Endpoints:**

For `/api/membership`:
```
{
    "id": "business_logic_payment_race_condition",
    "description": "Business Logic: Race condition in payment processing - multiple concurrent requests",
    "endpoint": "/api/membership",
    "method": "POST",
    "payload": {"number": "4111111111111111", "cvc": "123", "expiry": "12/25", "name": "User"},
    "auth_token": "VALID_TOKEN",
    "executed": false
}

{
    "id": "business_logic_negative_payment",
    "description": "Business Logic: Payment with negative amount to credit account instead of debit",
    "endpoint": "/api/membership",
    "method": "POST",
    "payload": {"number": "4111111111111111", "cvc": "123", "expiry": "12/25", "amount": -100},
    "auth_token": "VALID_TOKEN",
    "executed": false
}

{
    "id": "idor_payment_other_user_card",
    "description": "IDOR: User A attempts to use User B's stored payment method",
    "endpoint": "/api/membership",
    "method": "POST",
    "payload": {"user_id": "OTHER_USER_ID", "payment_method_id": "OTHER_USER_CARD"},
    "auth_token": "USER_A_TOKEN",
    "executed": false
}
```

**Debug/Admin Endpoints:**

For `/api/debug`:
```
{
    "id": "privilege_escalation_debug_access",
    "description": "Privilege Escalation: Regular user accessing debug endpoint for command execution",
    "endpoint": "/api/debug",
    "method": "POST",
    "payload": {"body": {"command": "whoami"}},
    "auth_token": "REGULAR_USER_TOKEN",
    "executed": false
}

{
    "id": "business_logic_debug_unauthenticated",
    "description": "Business Logic: Unauthenticated access to debug endpoint",
    "endpoint": "/api/debug",
    "method": "POST",
    "payload": {"body": {"command": "env"}},
    "auth_token": null,
    "executed": false
}
```

🔥 **ADVANCED BUSINESS LOGIC SCENARIOS**

**Multi-Step Attack Chains:**
Create scenarios that simulate real-world attack patterns:

1. **Account Takeover Chain**:
   - IDOR to access victim's profile
   - Mass assignment to escalate privileges
   - Access admin functions with elevated account

2. **Financial Fraud Chain**:
   - Race condition to duplicate payments
   - IDOR to access other users' payment methods
   - Business logic bypass to credit accounts

3. **Data Exfiltration Chain**:
   - Function-level bypass to access user data
   - IDOR to enumerate all user profiles
   - Privilege escalation to access admin data

**State Manipulation Scenarios:**
```
{
    "id": "toctou_user_profile_update",
    "description": "TOCTOU: Time-of-check to time-of-use attack on user profile validation",
    "endpoint": "/api/user",
    "method": "PUT",
    "payload": {"user": {"admin": true}, "validation_bypass": true},
    "auth_token": "VALID_TOKEN",
    "executed": false
}

{
    "id": "session_state_manipulation",
    "description": "Session State: Manipulate session state to bypass authorization checks",
    "endpoint": "/api/articles/feed",
    "method": "GET",
    "payload": null,
    "auth_token": "MANIPULATED_SESSION_TOKEN",
    "executed": false
}
```

**Bulk Operation Abuse:**
```
{
    "id": "bulk_operation_privilege_abuse",
    "description": "Bulk Operation: Use bulk operations to bypass individual authorization checks",
    "endpoint": "/api/articles",
    "method": "POST",
    "payload": {"bulk_create": [{"title": "Article 1"}, {"title": "Article 2"}], "bypass_auth": true},
    "auth_token": "LIMITED_USER_TOKEN",
    "executed": false
}
```

🔥 **BUSINESS CONTEXT UNDERSTANDING**

**Authentication Context Scenarios:**
- Test every protected endpoint without authentication
- Test with expired, invalid, and manipulated tokens
- Test cross-user token usage

**Authorization Context Scenarios:**
- Test regular users accessing admin endpoints
- Test cross-tenant data access
- Test resource ownership validation

**Business Logic Context Scenarios:**
- Test payment processing edge cases
- Test subscription/membership bypass attempts
- Test workflow state manipulation

**CRITICAL SUCCESS METRICS:**
- Create 100+ scenarios focused on business logic vulnerabilities
- Ensure 70% of scenarios target IDOR/BOLA vulnerabilities
- Include multi-step attack chain scenarios
- Test every endpoint for authorization bypass
- Create scenarios that require human-like reasoning to detect

**SCENARIO NAMING CONVENTION:**
- Start with vulnerability type: "idor_", "bola_", "business_logic_", "privilege_escalation_"
- Include target resource: "user_", "article_", "comment_", "payment_"
- Describe the attack: "cross_user_access", "ownership_bypass", "role_escalation"

The goal is to create scenarios that expose the subtle authorization and business logic flaws that make applications vulnerable to sophisticated attacks!
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