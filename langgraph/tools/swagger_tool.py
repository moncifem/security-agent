from langchain_core.tools import tool
from typing import Dict, Any
import requests
import json
import logging

logger = logging.getLogger(__name__)

@tool
def get_swagger(url: str) -> Dict[str, Any]:
    """Fetches and parses a Swagger/OpenAPI specification from a given URL.
    
    Args:
        url (str): The URL of the Swagger/OpenAPI specification
        
    Returns:
        Dict[str, Any]: The parsed Swagger/OpenAPI specification as a dictionary
    """
    logger.info(f"[SwaggerTool]: Fetching swagger from {url}")
    try:
        # Add headers for better compatibility
        headers = {
            'Accept': 'application/json, application/yaml, text/yaml',
            'User-Agent': 'Swagger-Parser/1.0'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Try to parse as JSON first
        try:
            swagger_data = response.json()
            logger.info("[SwaggerTool]: Successfully parsed JSON response")
        except json.JSONDecodeError:
            # If JSON parsing fails, try YAML (some swagger specs are in YAML)
            import yaml
            swagger_data = yaml.safe_load(response.text)
            logger.info("[SwaggerTool]: Successfully parsed YAML response")
        
        # Validate it's a valid OpenAPI/Swagger spec
        if not isinstance(swagger_data, dict):
            logger.error("[SwaggerTool]: Invalid swagger format - root is not an object")
            return {"error": "Invalid swagger format: root is not an object"}
            
        if "openapi" not in swagger_data and "swagger" not in swagger_data:
            logger.error("[SwaggerTool]: Invalid swagger format - missing openapi/swagger version")
            return {"error": "Invalid swagger format: missing openapi/swagger version"}
            
        # Extract key information for validation
        info = {
            "version": swagger_data.get("openapi") or swagger_data.get("swagger"),
            "title": swagger_data.get("info", {}).get("title", "Unknown"),
            "endpoints_count": len(swagger_data.get("paths", {})),
            "has_components": "components" in swagger_data,
            "has_definitions": "definitions" in swagger_data
        }
        
        return {
            "success": True,
            "data": swagger_data,
            "info": info,
            "url": url
        }
        
    except requests.exceptions.Timeout:
        return {"error": f"Timeout fetching swagger from {url}", "success": False}
    except requests.exceptions.ConnectionError:
        return {"error": f"Connection error fetching swagger from {url}", "success": False}
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP error {e.response.status_code} fetching swagger from {url}", "success": False}
    except requests.exceptions.RequestException as e:
        return {"error": f"Request error fetching swagger from {url}: {str(e)}", "success": False}
    except Exception as e:
        return {"error": f"Unexpected error parsing swagger from {url}: {str(e)}", "success": False}