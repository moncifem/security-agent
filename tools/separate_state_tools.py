"""
Specialized tools for separate state management
"""

import json
from typing import Dict, List, Any, Tuple
from tools.separate_states import EndpointsState, ScenariosState, ResultsState, VulnerabilitiesState, TestScenario, TestResult

# =====================================
# ENDPOINTS TOOLS
# =====================================

def load_endpoints_state() -> Tuple[int, str]:
    """Load endpoints state"""
    try:
        try:
            with open("endpoints_state.json", "r") as f:
                return 200, f.read()
        except FileNotFoundError:
            empty_state = EndpointsState()
            return 200, empty_state.to_json()
    except Exception as e:
        return 500, f"Error loading endpoints state: {str(e)}"

def save_endpoints_state(state_json: str) -> Tuple[int, str]:
    """Save endpoints state"""
    try:
        state = EndpointsState.from_json(state_json)
        with open("endpoints_state.json", "w") as f:
            f.write(state.to_json())
        return 200, "Endpoints state saved successfully"
    except Exception as e:
        return 500, f"Error saving endpoints state: {str(e)}"

def add_endpoint(endpoint: str) -> Tuple[int, str]:
    """Add an endpoint to endpoints state"""
    try:
        status, state_json = load_endpoints_state()
        if status != 200:
            return status, state_json
        
        state = EndpointsState.from_json(state_json)
        state.add_endpoint(endpoint)
        return save_endpoints_state(state.to_json())
    except Exception as e:
        return 500, f"Error adding endpoint: {str(e)}"

def get_endpoints() -> Tuple[int, str]:
    """Get all endpoints"""
    try:
        status, state_json = load_endpoints_state()
        if status != 200:
            return status, state_json
        
        state = EndpointsState.from_json(state_json)
        return 200, json.dumps(state.endpoints)
    except Exception as e:
        return 500, f"Error getting endpoints: {str(e)}"

def get_endpoints_count() -> Tuple[int, str]:
    """Get count of discovered endpoints"""
    try:
        status, state_json = load_endpoints_state()
        if status != 200:
            return status, state_json
        
        state = EndpointsState.from_json(state_json)
        return 200, json.dumps({"endpoints_count": state.get_count()})
    except Exception as e:
        return 500, f"Error getting endpoints count: {str(e)}"

# =====================================
# SCENARIOS TOOLS
# =====================================

def load_scenarios_state() -> Tuple[int, str]:
    """Load scenarios state"""
    try:
        try:
            with open("scenarios_state.json", "r") as f:
                return 200, f.read()
        except FileNotFoundError:
            empty_state = ScenariosState()
            return 200, empty_state.to_json()
    except Exception as e:
        return 500, f"Error loading scenarios state: {str(e)}"

def save_scenarios_state(state_json: str) -> Tuple[int, str]:
    """Save scenarios state"""
    try:
        state = ScenariosState.from_json(state_json)
        with open("scenarios_state.json", "w") as f:
            f.write(state.to_json())
        return 200, "Scenarios state saved successfully"
    except Exception as e:
        return 500, f"Error saving scenarios state: {str(e)}"

def add_test_scenario(scenario_data: Dict[str, Any]) -> Tuple[int, str]:
    """Add a test scenario"""
    try:
        status, state_json = load_scenarios_state()
        if status != 200:
            return status, state_json
        
        state = ScenariosState.from_json(state_json)
        scenario = TestScenario(
            id=scenario_data.get("id", ""),
            description=scenario_data.get("description", ""),
            endpoint=scenario_data.get("endpoint", ""),
            method=scenario_data.get("method", ""),
            payload=scenario_data.get("payload"),
            auth_token=scenario_data.get("auth_token"),
            executed=scenario_data.get("executed", False)
        )
        state.add_scenario(scenario)
        return save_scenarios_state(state.to_json())
    except Exception as e:
        return 500, f"Error adding test scenario: {str(e)}"

def get_pending_scenarios() -> Tuple[int, str]:
    """Get all pending (unexecuted) scenarios"""
    try:
        status, state_json = load_scenarios_state()
        if status != 200:
            return status, state_json
        
        state = ScenariosState.from_json(state_json)
        pending = state.get_pending_scenarios()
        pending_dicts = [
            {
                "id": s.id,
                "description": s.description,
                "endpoint": s.endpoint,
                "method": s.method,
                "payload": s.payload,
                "auth_token": s.auth_token,
                "executed": s.executed
            }
            for s in pending
        ]
        return 200, json.dumps(pending_dicts)
    except Exception as e:
        return 500, f"Error getting pending scenarios: {str(e)}"

def mark_scenario_executed(scenario_id: str) -> Tuple[int, str]:
    """Mark a scenario as executed"""
    try:
        status, state_json = load_scenarios_state()
        if status != 200:
            return status, state_json
        
        state = ScenariosState.from_json(state_json)
        state.mark_executed(scenario_id)
        return save_scenarios_state(state.to_json())
    except Exception as e:
        return 500, f"Error marking scenario as executed: {str(e)}"

def get_scenarios_summary() -> Tuple[int, str]:
    """Get scenarios execution summary"""
    try:
        status, state_json = load_scenarios_state()
        if status != 200:
            return status, state_json
        
        state = ScenariosState.from_json(state_json)
        summary = {
            "total_scenarios": state.get_total_count(),
            "executed_scenarios": state.get_executed_count(),
            "pending_scenarios": state.get_pending_count(),
            "execution_complete": state.is_complete()
        }
        return 200, json.dumps(summary)
    except Exception as e:
        return 500, f"Error getting scenarios summary: {str(e)}"

# =====================================
# RESULTS TOOLS
# =====================================

def load_results_state() -> Tuple[int, str]:
    """Load results state"""
    try:
        try:
            with open("results_state.json", "r") as f:
                return 200, f.read()
        except FileNotFoundError:
            empty_state = ResultsState()
            return 200, empty_state.to_json()
    except Exception as e:
        return 500, f"Error loading results state: {str(e)}"

def save_results_state(state_json: str) -> Tuple[int, str]:
    """Save results state"""
    try:
        state = ResultsState.from_json(state_json)
        with open("results_state.json", "w") as f:
            f.write(state.to_json())
        return 200, "Results state saved successfully"
    except Exception as e:
        return 500, f"Error saving results state: {str(e)}"

def add_test_result(result_data: Dict[str, Any]) -> Tuple[int, str]:
    """Add a test result"""
    try:
        status, state_json = load_results_state()
        if status != 200:
            return status, state_json
        
        state = ResultsState.from_json(state_json)
        result = TestResult(
            scenario_id=result_data.get("scenario_id", ""),
            status_code=result_data.get("status_code", 0),
            response_body=result_data.get("response_body", ""),
            success=result_data.get("success", False),
            details=result_data.get("details")
        )
        state.add_result(result)
        
        # Also mark the scenario as executed
        mark_scenario_executed(result.scenario_id)
        
        return save_results_state(state.to_json())
    except Exception as e:
        return 500, f"Error adding test result: {str(e)}"

def get_test_results() -> Tuple[int, str]:
    """Get all test results"""
    try:
        status, state_json = load_results_state()
        if status != 200:
            return status, state_json
        
        state = ResultsState.from_json(state_json)
        results_dicts = [
            {
                "scenario_id": r.scenario_id,
                "status_code": r.status_code,
                "response_body": r.response_body,
                "success": r.success,
                "details": r.details
            }
            for r in state.results
        ]
        return 200, json.dumps(results_dicts)
    except Exception as e:
        return 500, f"Error getting test results: {str(e)}"

def get_results_summary() -> Tuple[int, str]:
    """Get results summary"""
    try:
        status, state_json = load_results_state()
        if status != 200:
            return status, state_json
        
        state = ResultsState.from_json(state_json)
        summary = {
            "total_results": state.get_count(),
            "successful_tests": state.get_successful_count(),
            "failed_tests": state.get_failed_count()
        }
        return 200, json.dumps(summary)
    except Exception as e:
        return 500, f"Error getting results summary: {str(e)}"

# =====================================
# VULNERABILITIES TOOLS
# =====================================

def load_vulnerabilities_state() -> Tuple[int, str]:
    """Load vulnerabilities state"""
    try:
        try:
            with open("vulnerabilities_state.json", "r") as f:
                return 200, f.read()
        except FileNotFoundError:
            empty_state = VulnerabilitiesState()
            return 200, empty_state.to_json()
    except Exception as e:
        return 500, f"Error loading vulnerabilities state: {str(e)}"

def save_vulnerabilities_state(state_json: str) -> Tuple[int, str]:
    """Save vulnerabilities state"""
    try:
        state = VulnerabilitiesState.from_json(state_json)
        with open("vulnerabilities_state.json", "w") as f:
            f.write(state.to_json())
        return 200, "Vulnerabilities state saved successfully"
    except Exception as e:
        return 500, f"Error saving vulnerabilities state: {str(e)}"

def add_vulnerability(vuln_data: Dict[str, Any]) -> Tuple[int, str]:
    """Add a vulnerability"""
    try:
        status, state_json = load_vulnerabilities_state()
        if status != 200:
            return status, state_json
        
        state = VulnerabilitiesState.from_json(state_json)
        state.add_vulnerability(vuln_data)
        return save_vulnerabilities_state(state.to_json())
    except Exception as e:
        return 500, f"Error adding vulnerability: {str(e)}"

def get_vulnerabilities() -> Tuple[int, str]:
    """Get all vulnerabilities"""
    try:
        status, state_json = load_vulnerabilities_state()
        if status != 200:
            return status, state_json
        
        state = VulnerabilitiesState.from_json(state_json)
        return 200, json.dumps(state.vulnerabilities)
    except Exception as e:
        return 500, f"Error getting vulnerabilities: {str(e)}"

def get_vulnerabilities_summary() -> Tuple[int, str]:
    """Get vulnerabilities summary by severity"""
    try:
        status, state_json = load_vulnerabilities_state()
        if status != 200:
            return status, state_json
        
        state = VulnerabilitiesState.from_json(state_json)
        summary = {
            "total_vulnerabilities": state.get_count(),
            "high_severity": state.get_high_severity_count(),
            "medium_severity": state.get_medium_severity_count(),
            "low_severity": state.get_low_severity_count()
        }
        return 200, json.dumps(summary)
    except Exception as e:
        return 500, f"Error getting vulnerabilities summary: {str(e)}"

# =====================================
# EXECUTION TRACKING TOOLS
# =====================================

def check_execution_progress() -> Tuple[int, str]:
    """Check overall execution progress across all states"""
    try:
        # Get scenarios summary
        scenarios_status, scenarios_data = get_scenarios_summary()
        if scenarios_status != 200:
            return scenarios_status, scenarios_data
        scenarios_summary = json.loads(scenarios_data)
        
        # Get results summary
        results_status, results_data = get_results_summary()
        if results_status != 200:
            return results_status, results_data
        results_summary = json.loads(results_data)
        
        # Get vulnerabilities summary
        vulns_status, vulns_data = get_vulnerabilities_summary()
        if vulns_status != 200:
            return vulns_status, vulns_data
        vulns_summary = json.loads(vulns_data)
        
        # Get endpoints count
        endpoints_status, endpoints_data = get_endpoints_count()
        if endpoints_status != 200:
            return endpoints_status, endpoints_data
        endpoints_summary = json.loads(endpoints_data)
        
        progress = {
            "endpoints_discovered": endpoints_summary["endpoints_count"],
            "scenarios_planned": scenarios_summary["total_scenarios"],
            "scenarios_executed": scenarios_summary["executed_scenarios"],
            "scenarios_pending": scenarios_summary["pending_scenarios"],
            "execution_complete": scenarios_summary["execution_complete"],
            "total_test_results": results_summary["total_results"],
            "successful_tests": results_summary["successful_tests"],
            "failed_tests": results_summary["failed_tests"],
            "vulnerabilities_found": vulns_summary["total_vulnerabilities"],
            "high_severity_vulns": vulns_summary["high_severity"],
            "medium_severity_vulns": vulns_summary["medium_severity"],
            "low_severity_vulns": vulns_summary["low_severity"]
        }
        
        return 200, json.dumps(progress, indent=2)
    except Exception as e:
        return 500, f"Error checking execution progress: {str(e)}"

def is_testing_complete() -> Tuple[int, str]:
    """Simple check if all scenarios have been executed"""
    try:
        status, data = get_scenarios_summary()
        if status != 200:
            return status, data
        
        summary = json.loads(data)
        is_complete = summary["execution_complete"]
        
        result = {
            "testing_complete": is_complete,
            "scenarios_planned": summary["total_scenarios"],
            "scenarios_executed": summary["executed_scenarios"],
            "scenarios_remaining": summary["pending_scenarios"]
        }
        
        return 200, json.dumps(result)
    except Exception as e:
        return 500, f"Error checking if testing is complete: {str(e)}" 