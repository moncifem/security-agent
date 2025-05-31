import unittest
import os
import json
import yaml # Added for parsing YAML example files
from compact_api_docs import generate_compact_docs, detect_api_version # Removed get_api_spec

# Define the directory where example API specs are located
EXAMPLE_DIR = os.path.join(os.path.dirname(__file__), 'example')

class TestCompactApiDocs(unittest.TestCase):

    def _run_test_on_spec(self, file_name: str, expected_version_substring: str, min_endpoint_lines: int, min_type_lines: int):
        """Helper function to run common test steps on a spec file."""
        file_path = os.path.join(EXAMPLE_DIR, file_name)
        self.assertTrue(os.path.exists(file_path), f"Test file {file_path} not found.")

        api_data_content = None
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_name.lower().endswith(('.yaml', '.yml')):
                    api_data_content = yaml.safe_load(f)
                elif file_name.lower().endswith('.json'):
                    api_data_content = json.load(f)
                else:
                    self.fail(f"Unsupported file type for test: {file_name}")
            
            self.assertIsNotNone(api_data_content, f"Parsing {file_path} resulted in None. File might be empty or malformed.")

        except Exception as e:
            self.fail(f"Error reading or parsing test file {file_path}: {str(e)}")

        # api_data_content is now the parsed dictionary from the local file
        detected_version = detect_api_version(api_data_content)
        self.assertIsNotNone(detected_version, f"Could not detect version for {file_name}")
        self.assertIn(expected_version_substring, detected_version, f"Incorrect version detected for {file_name}")

        compact_docs = generate_compact_docs(api_data_content)
        self.assertIsNotNone(compact_docs, f"generate_compact_docs returned None for {file_name}")
        self.assertNotIn("❌ Error:", compact_docs, f"Error generating compact docs for {file_name}: {compact_docs}")

        # Check for key structural elements
        self.assertIn(f"(OAS {expected_version_substring})", compact_docs, "Version string missing in output")
        self.assertIn("## Endpoints", compact_docs, "'## Endpoints' section missing")
        self.assertIn("## Types", compact_docs, "'## Types' section missing")
        self.assertIn("🔒=auth ←=req →=resp", compact_docs, "Legend missing or incorrect")

        # Check for minimum content (very basic check)
        lines = compact_docs.splitlines()
        endpoint_section = False
        type_section = False
        actual_endpoint_lines = 0
        actual_type_lines = 0

        for line in lines:
            if line.startswith("## Endpoints"):
                endpoint_section = True
                type_section = False
                continue
            if line.startswith("## Types"):
                type_section = True
                endpoint_section = False
                continue
            
            if endpoint_section and line.strip() and not line.startswith("**") and not line.startswith("##"):
                actual_endpoint_lines += 1
            if type_section and line.strip() and not line.startswith("**") and not line.startswith("##"):
                actual_type_lines += 1
        
        self.assertGreaterEqual(actual_endpoint_lines, min_endpoint_lines, 
                                f"Expected at least {min_endpoint_lines} endpoint definition lines, found {actual_endpoint_lines} for {file_name}")
        self.assertGreaterEqual(actual_type_lines, min_type_lines, 
                                f"Expected at least {min_type_lines} type definition lines, found {actual_type_lines} for {file_name}")

        print(f"Successfully tested local file {file_name}. Output ({len(compact_docs)} chars):\n            {compact_docs[:200]}...") # Clarified source

    def test_swagger_v2_yaml(self):
        """Test with swagger-v2.yaml (Petstore)"""
        self._run_test_on_spec(
            file_name="swagger-v2.yaml", 
            expected_version_substring="2.0",
            min_endpoint_lines=10, # Based on Petstore v2 example
            min_type_lines=3       # Based on Petstore v2 example
        )

    def test_swagger_v3_yaml(self):
        """Test with swagger-v3.yaml (Petstore)"""
        self._run_test_on_spec(
            file_name="swagger-v3.yaml", 
            expected_version_substring="3.0",
            min_endpoint_lines=10, # Based on Petstore v3 example
            min_type_lines=3       # Based on Petstore v3 example
        )

    def test_swagger_v3_json(self):
        """Test with swagger-v3.json (Conduit/Realworld)"""
        # This is a different API (Conduit), so content checks will differ
        self._run_test_on_spec(
            file_name="swagger-v3.json", 
            expected_version_substring="3.0",
            min_endpoint_lines=15, # Based on Conduit example
            min_type_lines=5       # Based on Conduit example
        )

if __name__ == '__main__':
    unittest.main() 