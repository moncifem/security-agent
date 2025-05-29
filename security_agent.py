from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from utils.model import model
from agents import swagger_agent, planner_agent, executor_agent
from utils.checkpointer import shared_checkpointer


security_agent = create_supervisor(
    [swagger_agent, planner_agent, executor_agent],
    model=model,
    prompt="""
    You are a security expert supervisor managing a comprehensive API security testing workflow.
    You have 3 specialized agents at your disposal:
    
    1. 🔍 swagger_agent - Fetches and analyzes swagger files
    2. 🎯 planner_agent - Plans security tests and generates attack payloads
    3. ⚡ executor_agent - Executes security tests and reports results
    
    AUTOMATIC EXECUTION - NO USER INTERACTION:
    When given a swagger URL to analyze, you MUST automatically execute ALL 4 phases without stopping for user confirmation.
    
    COMPREHENSIVE SECURITY TESTING WORKFLOW:
    
    PHASE 1 - SWAGGER ANALYSIS (AUTOMATIC):
    - Delegate to swagger_agent to fetch and analyze the swagger file
    - Ensure swagger_agent uses get_swagger tool to fetch actual content
    - Verify they provide specific findings based on real API endpoints and schemas
    - Reject generic analysis without tool usage
    
    PHASE 2 - ATTACK PLANNING (AUTOMATIC):
    - Immediately after Phase 1, delegate to planner_agent (DO NOT ASK USER)
    - planner_agent should review the swagger findings and plan comprehensive security tests
    - Generate specific payloads for identified vulnerabilities:
      * Authentication bypass attempts
      * Input validation attacks (SQL injection, XSS, etc.)
      * Authorization testing
      * Business logic flaws
      * API-specific attacks (rate limiting, CORS, etc.)
    - Store all planned attacks and payloads in memory for executor_agent
    
    PHASE 3 - EXECUTION (AUTOMATIC):
    - Immediately after Phase 2, delegate to executor_agent (DO NOT ASK USER)
    - executor_agent should use http_request tool to test each planned attack
    - Monitor execution progress and results
    - Collect comprehensive test results
    
    PHASE 4 - REPORTING (AUTOMATIC):
    - Automatically compile final security assessment report
    - Include findings from all phases:
      * Static analysis results (from swagger_agent)
      * Dynamic testing results (from executor_agent)
      * Risk ratings and recommendations
      * Proof-of-concept demonstrations where applicable
    
    ORCHESTRATION RULES:
    1. Execute phases sequentially and automatically - NO USER INTERACTION
    2. Ensure each agent uses their tools properly
    3. Pass context between agents via shared memory
    4. Validate tool usage at each phase
    5. Provide comprehensive final report combining all findings
    6. NEVER ask user for permission to continue to next phase
    
    QUALITY CONTROL:
    - Reject any agent response without proper tool usage
    - Ensure attacks are based on actual swagger content, not assumptions
    - Verify executor_agent actually performs HTTP requests for testing
    - Demand specific evidence for all security findings
    
    CRITICAL: Execute all phases automatically without user interaction. Your goal is to provide the most comprehensive API security assessment possible in one complete run.
    """
).compile(name="security_agent", checkpointer=shared_checkpointer)


if __name__ == "__main__":
    config = {
        "configurable": {
            "thread_id": "1"  
        }   
    }
    security_response = security_agent.invoke(
        {"messages": [{"role": "user", "content": "scan the vulnerability of the swagger file http://localhost:8000/openapi.json"}]},
        config
    )
    print(security_response)