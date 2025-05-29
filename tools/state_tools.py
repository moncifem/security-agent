"""
State management tools for security testing agents
"""

import json
from typing import Dict, List, Any
from tools.state import SecurityTestState, TestScenario, TestResult


def load_state() -> tuple[int, str]:
    """
    Load the current security test state from memory
    
    Returns:
        tuple: (status_code, state_json)
    """
    try:
        # For now, use a simple file-based approach
        # In production, this would read from the actual checkpointer
        try:
            with open("current_state.json", "r") as f:
                state_json = f.read()
                return 200, state_json
        except FileNotFoundError:
            # Return empty state if file doesn't exist
            empty_state = SecurityTestState()
            return 200, empty_state.to_json()
    except Exception as e:
        return 500, f"Error loading state: {str(e)}"


def save_state(state_json: str) -> tuple[int, str]:
    """
    Save the security test state to memory
    
    Args:
        state_json: JSON string representation of SecurityTestState
        
    Returns:
        tuple: (status_code, message)
    """
    try:
        # Validate that it's valid state JSON
        state = SecurityTestState.from_json(state_json)
        
        # Save to file
        with open("current_state.json", "w") as f:
            f.write(state.to_json())
        
        return 200, "State saved successfully"
    except Exception as e:
        return 500, f"Error saving state: {str(e)}"


def add_endpoint(endpoint: str) -> tuple[int, str]:
    """
    Add an endpoint to the current state
    
    Args:
        endpoint: Endpoint in format "METHOD /path"
        
    Returns:
        tuple: (status_code, message)
    """
    try:
        # Load current state
        status, state_json = load_state()
        if status != 200:
            return status, state_json
            
        # Add endpoint
        state = SecurityTestState.from_json(state_json)
        state.add_endpoint(endpoint)
        
        # Save updated state
        return save_state(state.to_json())
    except Exception as e:
        return 500, f"Error adding endpoint: {str(e)}"


def add_test_scenario(scenario_data: Dict[str, Any]) -> tuple[int, str]:
    """
    Add a test scenario to the current state
    
    Args:
        scenario_data: Dict with keys: id, description, endpoint, method, payload, auth_token
        
    Returns:
        tuple: (status_code, message)
    """
    try:
        # Load current state
        status, state_json = load_state()
        if status != 200:
            return status, state_json
            
        # Create and add scenario
        state = SecurityTestState.from_json(state_json)
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
        
        # Save updated state
        return save_state(state.to_json())
    except Exception as e:
        return 500, f"Error adding test scenario: {str(e)}"


def add_test_result(result_data: Dict[str, Any]) -> tuple[int, str]:
    """
    Add a test result to the current state
    
    Args:
        result_data: Dict with keys: scenario_id, status_code, response_body, success, details
        
    Returns:
        tuple: (status_code, message)
    """
    try:
        # Load current state
        status, state_json = load_state()
        if status != 200:
            return status, state_json
            
        # Create and add result
        state = SecurityTestState.from_json(state_json)
        result = TestResult(
            scenario_id=result_data.get("scenario_id", ""),
            status_code=result_data.get("status_code", 0),
            response_body=result_data.get("response_body", ""),
            success=result_data.get("success", False),
            details=result_data.get("details")
        )
        state.add_result(result)
        
        # Save updated state
        return save_state(state.to_json())
    except Exception as e:
        return 500, f"Error adding test result: {str(e)}"


def add_vulnerability(vuln_data: Dict[str, Any]) -> tuple[int, str]:
    """
    Add a vulnerability to the current state
    
    Args:
        vuln_data: Dict with vulnerability information
        
    Returns:
        tuple: (status_code, message)
    """
    try:
        # Load current state
        status, state_json = load_state()
        if status != 200:
            return status, state_json
            
        # Add vulnerability
        state = SecurityTestState.from_json(state_json)
        state.add_vulnerability(vuln_data)
        
        # Save updated state
        return save_state(state.to_json())
    except Exception as e:
        return 500, f"Error adding vulnerability: {str(e)}"


def get_endpoints() -> tuple[int, str]:
    """
    Get all discovered endpoints
    
    Returns:
        tuple: (status_code, endpoints_json_list)
    """
    try:
        status, state_json = load_state()
        if status != 200:
            return status, state_json
            
        state = SecurityTestState.from_json(state_json)
        return 200, json.dumps(state.endpoints)
    except Exception as e:
        return 500, f"Error getting endpoints: {str(e)}"


def get_pending_scenarios() -> tuple[int, str]:
    """
    Get all pending test scenarios
    
    Returns:
        tuple: (status_code, scenarios_json_list)
    """
    try:
        status, state_json = load_state()
        if status != 200:
            return status, state_json
            
        state = SecurityTestState.from_json(state_json)
        pending = state.get_pending_scenarios()
        # Convert to dict format for JSON serialization
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


def get_test_results() -> tuple[int, str]:
    """
    Get all test results
    
    Returns:
        tuple: (status_code, results_json_list)
    """
    try:
        status, state_json = load_state()
        if status != 200:
            return status, state_json
            
        state = SecurityTestState.from_json(state_json)
        # Convert to dict format for JSON serialization
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


def get_vulnerabilities() -> tuple[int, str]:
    """
    Get all discovered vulnerabilities
    
    Returns:
        tuple: (status_code, vulnerabilities_json_list)
    """
    try:
        status, state_json = load_state()
        if status != 200:
            return status, state_json
            
        state = SecurityTestState.from_json(state_json)
        return 200, json.dumps(state.vulnerabilities)
    except Exception as e:
        return 500, f"Error getting vulnerabilities: {str(e)}"


def get_state_summary() -> tuple[int, str]:
    """
    Get a summary of the current state
    
    Returns:
        tuple: (status_code, summary_json)
    """
    try:
        status, state_json = load_state()
        if status != 200:
            return status, state_json
            
        state = SecurityTestState.from_json(state_json)
        summary = {
            "endpoints_count": len(state.endpoints),
            "scenarios_count": len(state.scenarios),
            "results_count": len(state.results),
            "vulnerabilities_count": len(state.vulnerabilities),
            "pending_scenarios_count": len(state.get_pending_scenarios())
        }
        return 200, json.dumps(summary)
    except Exception as e:
        return 500, f"Error getting state summary: {str(e)}" 