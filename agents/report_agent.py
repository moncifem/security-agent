from utils.model import model
from langgraph.prebuilt import create_react_agent
from utils.checkpointer import shared_checkpointer
from tools import get_test_results, get_vulnerabilities, get_endpoints, get_state_summary, load_state
from tools.state import SecurityTestState
from utils.pdf_generator import generate_security_pdf_report
import json

report_agent = create_react_agent(
    model=model,
    name="report_agent",
    tools=[get_test_results, get_vulnerabilities, get_endpoints, get_state_summary, load_state],
    prompt="""
You are a security vulnerability analyst and reporting specialist with state management capabilities.

Your job is to:
1. Use state management tools to read all test data from shared state
2. Analyze findings and categorize vulnerabilities by severity
3. Generate a comprehensive security assessment report

WORKFLOW:
1. Call get_state_summary to see overall testing statistics
2. Call get_endpoints to see all tested endpoints
3. Call get_test_results to analyze all test executions
4. Call get_vulnerabilities to review all discovered security issues
5. Provide comprehensive analysis and recommendations

ANALYSIS STRUCTURE:

1. **EXECUTIVE SUMMARY**
   - Total endpoints tested
   - Total tests executed  
   - Vulnerabilities found by severity (HIGH/MEDIUM/LOW)
   - Overall risk assessment

2. **DETAILED FINDINGS**
   - Each vulnerability with evidence
   - Impact analysis
   - Specific remediation steps

3. **COVERAGE ANALYSIS**
   - Endpoint coverage percentage
   - Test scenario completion
   - Areas needing additional testing

4. **RECOMMENDATIONS**
   - Immediate action items for HIGH severity issues
   - Long-term security improvements
   - Implementation timeline

VULNERABILITY CATEGORIZATION:

HIGH SEVERITY:
- Authentication bypass
- IDOR vulnerabilities  
- Successful injection attacks
- Privilege escalation
- Sensitive data exposure

MEDIUM SEVERITY:
- Information disclosure
- Debug endpoints accessible
- Weak input validation
- Missing security controls

LOW SEVERITY:
- Verbose error messages
- Missing security headers
- Minor configuration issues

REPORT FORMAT:
Provide a comprehensive text-based security assessment that includes:
- Executive summary with key statistics
- Detailed vulnerability descriptions with evidence
- Risk assessment and impact analysis
- Prioritized remediation recommendations
- Technical details for developers

Use the state management tools to gather all necessary data for the analysis.
""",
    checkpointer=shared_checkpointer
)

def generate_pdf_report_from_state():
    """Generate PDF report from current state data"""
    try:
        # Load current state
        from tools.state_tools import load_state
        status, state_json = load_state()
        
        if status != 200:
            print(f"❌ Failed to load state: {state_json}")
            return None
            
        # Parse state from JSON
        state = SecurityTestState.from_json(state_json)
        
        # Generate PDF using actual state data
        from utils.pdf_generator import SecurityReportPDF
        pdf_generator = SecurityReportPDF()
        
        timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = pdf_generator.generate_report(state, f"security_report_{timestamp}.pdf")
        
        print(f"📄 PDF Report Generated: {output_file}")
        return output_file
    except Exception as e:
        print(f"❌ Failed to generate PDF report: {e}")
        return None

if __name__ == "__main__":
    # Example invocation
    config = {
        "configurable": {"thread_id": "security_test_session"}
    }
    
    # Generate vulnerability analysis report
    report_result = report_agent.invoke({
        "messages": [{"role": "user", "content": "Generate a comprehensive security vulnerability report based on all test results and findings in memory."}]
    }, config)
    
    print("📊 Security Report Generated:")
    print(report_result) 