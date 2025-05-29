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

class SecurityTestState:
    """Manages the complete state of security testing across agents"""
    
    def __init__(self):
        self.endpoints: List[str] = []
        self.scenarios: List[TestScenario] = []
        self.results: List[TestResult] = []
        self.vulnerabilities: List[Dict[str, Any]] = []
        self.auth_tokens: Dict[str, str] = {}
        
    def add_endpoint(self, endpoint: str):
        """Add a discovered endpoint"""
        if endpoint not in self.endpoints:
            self.endpoints.append(endpoint)
    
    def add_scenario(self, scenario: TestScenario):
        """Add a test scenario"""
        self.scenarios.append(scenario)
    
    def add_result(self, result: TestResult):
        """Add a test result and mark scenario as executed"""
        self.results.append(result)
        # Mark the corresponding scenario as executed
        for scenario in self.scenarios:
            if scenario.id == result.scenario_id:
                scenario.executed = True
                break
    
    def get_pending_scenarios(self) -> List[TestScenario]:
        """Get scenarios that haven't been executed yet"""
        return [s for s in self.scenarios if not s.executed]
    
    def add_vulnerability(self, vuln: Dict[str, Any]):
        """Add a discovered vulnerability"""
        self.vulnerabilities.append(vuln)
    
    def set_auth_token(self, user: str, token: str):
        """Store authentication token"""
        self.auth_tokens[user] = token
    
    def to_json(self) -> str:
        """Serialize state to JSON"""
        return json.dumps({
            "endpoints": self.endpoints,
            "scenarios": [asdict(s) for s in self.scenarios],
            "results": [asdict(r) for r in self.results],
            "vulnerabilities": self.vulnerabilities,
            "auth_tokens": self.auth_tokens
        }, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'SecurityTestState':
        """Deserialize state from JSON"""
        state = cls()
        if not json_str or json_str == "{}":
            return state
            
        try:
            data = json.loads(json_str)
            state.endpoints = data.get("endpoints", [])
            state.vulnerabilities = data.get("vulnerabilities", [])
            state.auth_tokens = data.get("auth_tokens", {})
            
            # Reconstruct scenarios
            for s_data in data.get("scenarios", []):
                scenario = TestScenario(**s_data)
                state.scenarios.append(scenario)
            
            # Reconstruct results
            for r_data in data.get("results", []):
                result = TestResult(**r_data)
                state.results.append(result)
                
        except json.JSONDecodeError:
            pass  # Return empty state if JSON is invalid
            
        return state
