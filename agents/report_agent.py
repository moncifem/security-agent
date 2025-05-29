from utils.model import model
from langgraph.prebuilt import create_react_agent
from utils.checkpointer import shared_checkpointer
from tools import (
    get_test_results, get_vulnerabilities, get_endpoints, 
    get_scenarios_summary, get_results_summary, get_vulnerabilities_summary,
    check_execution_progress, is_testing_complete
)
from tools.separate_states import EndpointsState, ScenariosState, ResultsState, VulnerabilitiesState
from utils.pdf_generator import generate_security_pdf_report
import json

report_agent = create_react_agent(
    model=model,
    name="report_agent",
    tools=[
        get_test_results, get_vulnerabilities, get_endpoints,
        get_scenarios_summary, get_results_summary, get_vulnerabilities_summary,
        check_execution_progress, is_testing_complete
    ],
    prompt="""
You are a security vulnerability analyst and reporting specialist with separate state management capabilities.

Your job is to:
1. Use state management tools to read all test data from separate focused states
2. Analyze findings and categorize vulnerabilities by severity
3. Generate a comprehensive security assessment report
4. Verify testing completion before finalizing the report

WORKFLOW:
1. Call is_testing_complete to verify all scenarios have been executed
2. Call check_execution_progress to get overall testing statistics
3. Call get_test_results to analyze all test executions
4. Call get_vulnerabilities to review all discovered security issues
5. Call get_vulnerabilities_summary for severity breakdown
6. Provide comprehensive analysis and recommendations

IMPORTANT: Before generating the final report, you MUST:
- Call is_testing_complete to ensure all planned scenarios have been executed
- If testing is incomplete, note this in your report and recommend completing remaining tests

ANALYSIS STRUCTURE:

1. **EXECUTION COMPLETENESS CHECK**
   - Verify all scenarios have been executed
   - Report any incomplete testing

2. **EXECUTIVE SUMMARY**
   - Total endpoints tested
   - Total tests executed  
   - Vulnerabilities found by severity (HIGH/MEDIUM/LOW)
   - Overall risk assessment

3. **DETAILED FINDINGS**
   - Each vulnerability with evidence
   - Impact analysis
   - Specific remediation steps

4. **COVERAGE ANALYSIS**
   - Endpoint coverage percentage
   - Test scenario completion status
   - Areas needing additional testing

5. **RECOMMENDATIONS**
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
- Testing completion status
- Executive summary with key statistics
- Detailed vulnerability descriptions with evidence
- Risk assessment and impact analysis
- Prioritized remediation recommendations
- Technical details for developers

The separate state system allows for more focused analysis of each data type!
""",
    checkpointer=shared_checkpointer
)

def generate_pdf_report_from_separate_states():
    """Generate PDF report from current separate state data"""
    try:
        # Load all separate states
        from tools.separate_state_tools import (
            load_endpoints_state, load_scenarios_state, 
            load_results_state, load_vulnerabilities_state
        )
        
        # Load each state
        endpoints_status, endpoints_json = load_endpoints_state()
        scenarios_status, scenarios_json = load_scenarios_state()
        results_status, results_json = load_results_state()
        vulns_status, vulns_json = load_vulnerabilities_state()
        
        if any(status != 200 for status in [endpoints_status, scenarios_status, results_status, vulns_status]):
            print("❌ Failed to load one or more state files")
            return None
        
        # Parse states
        endpoints_state = EndpointsState.from_json(endpoints_json)
        scenarios_state = ScenariosState.from_json(scenarios_json)
        results_state = ResultsState.from_json(results_json)
        vulns_state = VulnerabilitiesState.from_json(vulns_json)
        
        # Create a combined state object for PDF generation (backwards compatibility)
        combined_state = type('CombinedState', (), {
            'endpoints': endpoints_state.endpoints,
            'scenarios': scenarios_state.scenarios,
            'results': results_state.results,
            'vulnerabilities': vulns_state.vulnerabilities
        })()
        
        # Generate PDF using actual state data
        from utils.pdf_generator import SecurityReportPDF
        pdf_generator = SecurityReportPDF()
        
        timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = pdf_generator.generate_report(combined_state, f"security_report_{timestamp}.pdf")
        
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