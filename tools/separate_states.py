"""
Separate state management for easier LLM processing
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class TestScenario:
    """Represents a single test scenario"""
    id: str
    description: str
    endpoint: str
    method: str
    payload: Optional[Dict[str, Any]] = None
    auth_token: Optional[str] = None
    executed: bool = False

@dataclass
class TestResult:
    """Represents the result of executing a test scenario"""
    scenario_id: str
    status_code: int
    response_body: str
    success: bool
    details: Optional[str] = None

class EndpointsState:
    """Manages discovered API endpoints"""
    
    def __init__(self):
        self.endpoints: List[str] = []
    
    def add_endpoint(self, endpoint: str):
        """Add a discovered endpoint"""
        if endpoint not in self.endpoints:
            self.endpoints.append(endpoint)
    
    def get_count(self) -> int:
        """Get total number of endpoints"""
        return len(self.endpoints)
    
    def to_json(self) -> str:
        """Serialize to JSON"""
        return json.dumps({"endpoints": self.endpoints}, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'EndpointsState':
        """Deserialize from JSON"""
        state = cls()
        if json_str and json_str != "{}":
            try:
                data = json.loads(json_str)
                state.endpoints = data.get("endpoints", [])
            except json.JSONDecodeError:
                pass
        return state

class ScenariosState:
    """Manages test scenarios"""
    
    def __init__(self):
        self.scenarios: List[TestScenario] = []
    
    def add_scenario(self, scenario: TestScenario):
        """Add a test scenario"""
        self.scenarios.append(scenario)
    
    def mark_executed(self, scenario_id: str):
        """Mark a scenario as executed"""
        for scenario in self.scenarios:
            if scenario.id == scenario_id:
                scenario.executed = True
                break
    
    def get_pending_scenarios(self) -> List[TestScenario]:
        """Get scenarios that haven't been executed yet"""
        return [s for s in self.scenarios if not s.executed]
    
    def get_executed_scenarios(self) -> List[TestScenario]:
        """Get scenarios that have been executed"""
        return [s for s in self.scenarios if s.executed]
    
    def get_total_count(self) -> int:
        """Get total number of scenarios"""
        return len(self.scenarios)
    
    def get_pending_count(self) -> int:
        """Get number of pending scenarios"""
        return len(self.get_pending_scenarios())
    
    def get_executed_count(self) -> int:
        """Get number of executed scenarios"""
        return len(self.get_executed_scenarios())
    
    def is_complete(self) -> bool:
        """Check if all scenarios have been executed"""
        return self.get_pending_count() == 0
    
    def to_json(self) -> str:
        """Serialize to JSON"""
        return json.dumps({
            "scenarios": [asdict(s) for s in self.scenarios]
        }, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ScenariosState':
        """Deserialize from JSON"""
        state = cls()
        if json_str and json_str != "{}":
            try:
                data = json.loads(json_str)
                for s_data in data.get("scenarios", []):
                    scenario = TestScenario(**s_data)
                    state.scenarios.append(scenario)
            except json.JSONDecodeError:
                pass
        return state

class ResultsState:
    """Manages test execution results"""
    
    def __init__(self):
        self.results: List[TestResult] = []
    
    def add_result(self, result: TestResult):
        """Add a test result"""
        self.results.append(result)
    
    def get_count(self) -> int:
        """Get total number of results"""
        return len(self.results)
    
    def get_successful_count(self) -> int:
        """Get number of successful tests"""
        return len([r for r in self.results if r.success])
    
    def get_failed_count(self) -> int:
        """Get number of failed tests"""
        return len([r for r in self.results if not r.success])
    
    def get_results_for_scenario(self, scenario_id: str) -> List[TestResult]:
        """Get all results for a specific scenario"""
        return [r for r in self.results if r.scenario_id == scenario_id]
    
    def to_json(self) -> str:
        """Serialize to JSON"""
        return json.dumps({
            "results": [asdict(r) for r in self.results]
        }, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ResultsState':
        """Deserialize from JSON"""
        state = cls()
        if json_str and json_str != "{}":
            try:
                data = json.loads(json_str)
                for r_data in data.get("results", []):
                    result = TestResult(**r_data)
                    state.results.append(result)
            except json.JSONDecodeError:
                pass
        return state

class VulnerabilitiesState:
    """Manages discovered vulnerabilities"""
    
    def __init__(self):
        self.vulnerabilities: List[Dict[str, Any]] = []
    
    def add_vulnerability(self, vuln: Dict[str, Any]):
        """Add a discovered vulnerability"""
        self.vulnerabilities.append(vuln)
    
    def get_count(self) -> int:
        """Get total number of vulnerabilities"""
        return len(self.vulnerabilities)
    
    def get_by_severity(self, severity: str) -> List[Dict[str, Any]]:
        """Get vulnerabilities by severity level"""
        return [v for v in self.vulnerabilities if v.get('severity', '').upper() == severity.upper()]
    
    def get_high_severity_count(self) -> int:
        """Get number of HIGH severity vulnerabilities"""
        return len(self.get_by_severity('HIGH'))
    
    def get_medium_severity_count(self) -> int:
        """Get number of MEDIUM severity vulnerabilities"""
        return len(self.get_by_severity('MEDIUM'))
    
    def get_low_severity_count(self) -> int:
        """Get number of LOW severity vulnerabilities"""
        return len(self.get_by_severity('LOW'))
    
    def to_json(self) -> str:
        """Serialize to JSON"""
        return json.dumps({
            "vulnerabilities": self.vulnerabilities
        }, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'VulnerabilitiesState':
        """Deserialize from JSON"""
        state = cls()
        if json_str and json_str != "{}":
            try:
                data = json.loads(json_str)
                state.vulnerabilities = data.get("vulnerabilities", [])
            except json.JSONDecodeError:
                pass
        return state 