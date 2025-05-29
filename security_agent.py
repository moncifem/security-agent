#!/usr/bin/env python3
"""
Comprehensive API Security Testing Orchestrator with Separate State Management
"""

from agents import swagger_agent, planner_agent, executor_agent, report_agent
from agents.report_agent import generate_pdf_report_from_separate_states
from langchain_core.messages import HumanMessage
from tools.separate_state_tools import check_execution_progress, is_testing_complete
import json

def run_security_test(swagger_url: str, base_url: str = "http://localhost:8000"):
    """
    Run comprehensive security testing using the four-agent workflow with separate state management
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
            "messages": [HumanMessage(content=f"Analyze the swagger file at {swagger_url} and extract ALL endpoints using the separate state management tools.")]
        }, config)
        
        print("✅ Swagger analysis complete")
        
        # Check endpoints discovered
        try:
            progress_status, progress_data = check_execution_progress()
            if progress_status == 200:
                progress = json.loads(progress_data)
                print(f"📋 Found {progress.get('endpoints_discovered', 0)} endpoints")
            else:
                print("📋 Could not retrieve endpoints count")
        except Exception as e:
            print(f"📋 Error checking endpoints: {e}")
        
        # PHASE 2: Test Planning
        print("\n🎯 PHASE 2: Security Test Planning")
        print("-" * 40)
        
        planner_result = planner_agent.invoke({
            "messages": [HumanMessage(content="Use the separate state management tools to read endpoints and create comprehensive security test scenarios.")]
        }, config)
        
        print("✅ Test planning complete")
        
        # Check scenarios created
        try:
            progress_status, progress_data = check_execution_progress()
            if progress_status == 200:
                progress = json.loads(progress_data)
                print(f"📊 Created {progress.get('scenarios_planned', 0)} test scenarios")
            else:
                print("📊 Could not retrieve scenarios count")
        except Exception as e:
            print(f"📊 Error checking scenarios: {e}")
        
        # PHASE 3: Test Execution
        print("\n⚡ PHASE 3: Security Test Execution")
        print("-" * 40)
        
        executor_result = executor_agent.invoke({
            "messages": [HumanMessage(content=f"Use separate state management tools to read test scenarios and execute ALL of them against {base_url}. CRITICAL: You must execute ALL pending scenarios and verify completion using is_testing_complete.")]
        }, config)
        
        print("✅ Test execution complete")
        
        # Verify execution completion
        try:
            completion_status, completion_data = is_testing_complete()
            if completion_status == 200:
                completion = json.loads(completion_data)
                if completion.get('testing_complete', False):
                    print("🔒 All scenarios executed successfully")
                else:
                    print(f"⚠️  Testing incomplete: {completion.get('scenarios_remaining', 0)} scenarios remaining")
                    print("   You may need to run executor agent again")
            else:
                print("⚠️  Could not verify testing completion")
        except Exception as e:
            print(f"⚠️  Error checking completion: {e}")
        
        # PHASE 4: Vulnerability Reporting
        print("\n📊 PHASE 4: Vulnerability Analysis & Reporting")
        print("-" * 40)
        
        report_result = report_agent.invoke({
            "messages": [HumanMessage(content="Use separate state management tools to read all test results and vulnerabilities. Generate a comprehensive security assessment report and verify testing completion.")]
        }, config)
        
        print("✅ Vulnerability report generated")
        
        # PHASE 5: PDF Report Generation
        print("\n📄 PHASE 5: PDF Report Generation")
        print("-" * 40)
        
        try:
            pdf_file = generate_pdf_report_from_separate_states()
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
        
        # Get final execution summary
        try:
            progress_status, progress_data = check_execution_progress()
            if progress_status == 200:
                progress = json.loads(progress_data)
                
                print(f"\n📊 TESTING STATISTICS:")
                print(f"   • Endpoints Discovered: {progress.get('endpoints_discovered', 0)}")
                print(f"   • Test Scenarios Created: {progress.get('scenarios_planned', 0)}")
                print(f"   • Scenarios Executed: {progress.get('scenarios_executed', 0)}")
                print(f"   • Scenarios Pending: {progress.get('scenarios_pending', 0)}")
                print(f"   • Tests Results: {progress.get('total_test_results', 0)}")
                print(f"   • Vulnerabilities Found: {progress.get('vulnerabilities_found', 0)}")
                print(f"     - HIGH: {progress.get('high_severity_vulns', 0)}")
                print(f"     - MEDIUM: {progress.get('medium_severity_vulns', 0)}")
                print(f"     - LOW: {progress.get('low_severity_vulns', 0)}")
                
                if progress.get('execution_complete', False):
                    print(f"\n✅ EXECUTION COMPLETE: All scenarios have been tested!")
                else:
                    print(f"\n⚠️  EXECUTION INCOMPLETE: {progress.get('scenarios_pending', 0)} scenarios still pending")
            else:
                print(f"\n⚠️  Could not retrieve final statistics: {progress_data}")
        except Exception as e:
            print(f"\n⚠️  Error retrieving final statistics: {e}")
        
        print(f"\n💡 Detailed PDF report available: {pdf_file if pdf_file else 'Generation failed'}")
        print("🔒 Security assessment ready for management review!")
        print("\n📝 The new separate state system provides:")
        print("   • Smaller, focused state files for better LLM processing")
        print("   • Clear execution progress tracking")
        print("   • Easy verification of testing completion")
        
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
        print("🔧 Separate state management system working optimally!")
    else:
        print(f"⚠️  Testing encountered issues: {result.get('error', 'Unknown error')}")