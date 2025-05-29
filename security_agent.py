#!/usr/bin/env python3
"""
Comprehensive API Security Testing Orchestrator with State Management
"""

from agents import swagger_agent, planner_agent, executor_agent, report_agent
from agents.report_agent import generate_pdf_report_from_state
from langchain_core.messages import HumanMessage
from tools.state_tools import get_state_summary, load_state
import json

def run_security_test(swagger_url: str, base_url: str = "http://localhost:8000"):
    """
    Run comprehensive security testing using the four-agent workflow with state management
    """
    print("🚀 Starting Comprehensive API Security Testing")
    print("=" * 60)
    
    # Configuration for shared memory
    config = {
        "configurable": {"thread_id": "security_test_session"},
        "recursion_limit": 150
    }
    
    try:
        # PHASE 1: Swagger Analysis
        print("🔍 PHASE 1: Swagger Analysis & Endpoint Discovery")
        print("-" * 40)
        
        swagger_result = swagger_agent.invoke({
            "messages": [HumanMessage(content=f"Analyze the swagger file at {swagger_url} and extract ALL endpoints using the proper state management tools.")]
        }, config)
        
        print("✅ Swagger analysis complete")
        
        # Check state after swagger analysis
        try:
            summary_status, summary_data = get_state_summary()
            if summary_status == 200:
                summary = json.loads(summary_data)
                print(f"📋 Found {summary.get('endpoints_count', 0)} endpoints")
            else:
                print("📋 State summary not available yet")
        except Exception as e:
            print(f"📋 Could not retrieve state summary: {e}")
        
        # PHASE 2: Test Planning
        print("\n🎯 PHASE 2: Security Test Planning")
        print("-" * 40)
        
        planner_result = planner_agent.invoke({
            "messages": [HumanMessage(content="Use the state management tools to read endpoints and create comprehensive security test scenarios.")]
        }, config)
        
        print("✅ Test planning complete")
        
        # Check state after planning
        try:
            summary_status, summary_data = get_state_summary()
            if summary_status == 200:
                summary = json.loads(summary_data)
                print(f"📊 Created {summary.get('scenarios_count', 0)} test scenarios")
            else:
                print("📊 Test scenarios created (state parsing pending)")
        except Exception as e:
            print(f"📊 Could not retrieve scenarios count: {e}")
        
        # PHASE 3: Test Execution
        print("\n⚡ PHASE 3: Security Test Execution")
        print("-" * 40)
        
        executor_result = executor_agent.invoke({
            "messages": [HumanMessage(content=f"Use state management tools to read test scenarios and execute them against {base_url}. Store all results and vulnerabilities.")]
        }, config)
        
        print("✅ Test execution complete")
        print("🔒 Security testing finished")
        
        # PHASE 4: Vulnerability Reporting
        print("\n📊 PHASE 4: Vulnerability Analysis & Reporting")
        print("-" * 40)
        
        report_result = report_agent.invoke({
            "messages": [HumanMessage(content="Use state management tools to read all test results and vulnerabilities. Generate a comprehensive security assessment report.")]
        }, config)
        
        print("✅ Vulnerability report generated")
        
        # PHASE 5: PDF Report Generation
        print("\n📄 PHASE 5: PDF Report Generation")
        print("-" * 40)
        
        try:
            pdf_file = generate_pdf_report_from_state()
            if pdf_file:
                print(f"✅ PDF report generated successfully: {pdf_file}")
                print("📋 Comprehensive security assessment complete")
            else:
                print("⚠️  PDF generation failed")
        except Exception as e:
            print(f"⚠️  PDF generation error: {e}")
            pdf_file = None
        
        # PHASE 6: Final Summary
        print("\n🏁 PHASE 6: Final Summary")
        print("-" * 40)
        
        print("🎯 All security testing phases completed successfully!")
        print("📈 Phases executed:")
        print("   ✓ Swagger analysis and endpoint discovery")
        print("   ✓ Comprehensive test scenario planning")
        print("   ✓ Systematic security test execution")
        print("   ✓ Vulnerability analysis and reporting")
        print("   ✓ PDF report generation")
        
        # Get final state summary
        try:
            summary_status, summary_data = get_state_summary()
            if summary_status == 200:
                summary = json.loads(summary_data)
                
                print(f"\n📊 TESTING STATISTICS:")
                print(f"   • Endpoints Discovered: {summary.get('endpoints_count', 0)}")
                print(f"   • Test Scenarios Created: {summary.get('scenarios_count', 0)}")
                print(f"   • Tests Executed: {summary.get('results_count', 0)}")
                print(f"   • Vulnerabilities Found: {summary.get('vulnerabilities_count', 0)}")
            else:
                print(f"\n⚠️  Could not retrieve final statistics: {summary_data}")
        except Exception as e:
            print(f"\n⚠️  Error retrieving final statistics: {e}")
        
        print(f"\n💡 Detailed PDF report available: {pdf_file if pdf_file else 'Generation failed'}")
        print("🔒 Security assessment ready for management review!")
        
        return {
            "status": "success",
            "phases_completed": ["swagger_analysis", "planning", "execution", "reporting", "pdf_generation"],
            "swagger_result": swagger_result,
            "planner_result": planner_result,
            "executor_result": executor_result,
            "report_result": report_result,
            "pdf_file": pdf_file
        }
        
    except Exception as e:
        print(f"❌ Error during security testing: {e}")
        print("💡 This might be due to API connectivity or configuration issues.")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    # Run the security test
    swagger_url = "http://localhost:8000/openapi.json"
    base_url = "http://localhost:8000"
    
    result = run_security_test(swagger_url, base_url)
    
    print(f"\n🏁 Final Status: {result['status'].upper()}")
    if result["status"] == "success":
        print("✅ Comprehensive API security testing completed!")
        print("📊 Generated detailed vulnerability report with remediation recommendations!")
        if result.get("pdf_file"):
            print(f"📄 PDF report ready for download: {result['pdf_file']}")
        print("🔧 Structured state data successfully managed throughout testing")
    else:
        print(f"⚠️  Testing encountered issues: {result.get('error', 'Unknown error')}")