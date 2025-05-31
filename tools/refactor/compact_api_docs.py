#!/usr/bin/env python3
"""
Ultra-Compact API Documentation Generator
Supports Swagger 2.0, OpenAPI 3.0.x, OpenAPI 3.1.x (URL input for JSON or YAML)
Optimized for LLM context windows and large APIs. Output to STDOUT.
"""

import requests
import json
import sys
import yaml
from typing import Dict, Any, List, Optional, Tuple

ERROR_PREFIX = "❌ Error:"

def get_api_spec(url: str) -> Tuple[Optional[Dict[Any, Any]], Optional[str]]:
    """Fetch and parse API spec from URL. Returns (data, None) or (None, error_message)."""
    try:
        if not url.startswith(('http://', 'https://')):
            return None, f"{ERROR_PREFIX} Invalid URL: {url}. Only HTTP/HTTPS URLs are supported."
        response = requests.get(url, timeout=30)
        response.raise_for_status() 
        content_type = response.headers.get('Content-Type', '').lower()
        
        if 'application/json' in content_type or url.lower().endswith('.json'):
            return response.json(), None
        elif 'yaml' in content_type or 'x-yaml' in content_type or url.lower().endswith(('.yaml', '.yml')):
             return yaml.safe_load(response.text), None
        else:
            try:
                return response.json(), None
            except json.JSONDecodeError:
                try:
                    return yaml.safe_load(response.text), None
                except yaml.YAMLError:
                    return None, f"{ERROR_PREFIX} Could not determine content type or parse content from URL: {url}"

    except requests.exceptions.RequestException as e:
        return None, f"{ERROR_PREFIX} Error fetching API spec from URL {url}: {str(e)}"
    except json.JSONDecodeError as e:
        return None, f"{ERROR_PREFIX} Error decoding JSON from URL {url}: {str(e)}"
    except yaml.YAMLError as e:
        return None, f"{ERROR_PREFIX} Error decoding YAML from URL {url}: {str(e)}"
    except Exception as e:
        return None, f"{ERROR_PREFIX} An unexpected error occurred while processing URL {url}: {str(e)}"

def detect_api_version(api_data: Dict[Any, Any]) -> Optional[str]:
    """Detects the API specification version."""
    if api_data.get("swagger") == "2.0":
        return "2.0"
    if isinstance(api_data.get("openapi"), str):
        if api_data["openapi"].startswith("3.0."):
            return "3.0"
        if api_data["openapi"].startswith("3.1."):
            return "3.1"
    return None

def get_spec_components(api_data: Dict[Any, Any], version: str) -> Tuple[Dict, Dict, Dict]:
    """Gets paths, schemas, and security schemes based on API version."""
    paths = api_data.get("paths", {})
    if version == "2.0":
        schemas = api_data.get("definitions", {})
        security_schemes = api_data.get("securityDefinitions", {})
    elif version in ["3.0", "3.1"]:
        components = api_data.get("components", {})
        schemas = components.get("schemas", {})
        security_schemes = components.get("securitySchemes", {})
    else:
        schemas, security_schemes = {}, {}
    return paths, schemas, security_schemes

def extract_compact_type(schema_obj: Optional[Dict[Any, Any]], schemas_dict: Dict[Any, Any], version: str) -> str:
    """Extract a compact type representation from a schema object."""
    if not schema_obj: return "?"

    if "$ref" in schema_obj:
        ref_path = schema_obj["$ref"]
        if version == "2.0" and ref_path.startswith("#/definitions/"):
            return ref_path.split("/")[-1]
        if version in ["3.0", "3.1"] and ref_path.startswith("#/components/schemas/"):
            return ref_path.split("/")[-1]
        return ref_path.split("/")[-1]

    if version in ["3.0", "3.1"] and "anyOf" in schema_obj:
        types = [extract_compact_type(s, schemas_dict, version) for s in schema_obj["anyOf"]]
        result = "|".join(filter(None, types))
        return result[:15] + "..." if len(result) > 15 else result
    
    if version in ["3.0", "3.1"] and "oneOf" in schema_obj:
        types = [extract_compact_type(s, schemas_dict, version) for s in schema_obj["oneOf"]]
        result = "|".join(filter(None, types))
        return result[:15] + "..." if len(result) > 15 else result

    schema_type = schema_obj.get("type")
    if schema_type == "array":
        items = schema_obj.get("items", {})
        item_type = extract_compact_type(items, schemas_dict, version)
        return f"{item_type}[]"
    
    if schema_type: return str(schema_type)
    if schema_obj.get("properties") or schema_obj.get("additionalProperties"): return "obj"
    
    return "any"

def get_simple_type(prop_def: Dict[Any, Any], schemas: Dict[Any, Any], version: str) -> str:
    """Get a simple type representation for properties."""
    if "$ref" in prop_def:
        return extract_compact_type(prop_def, schemas, version)
    
    prop_type = prop_def.get("type", "?")
    if prop_type == "array":
        items = prop_def.get("items", {})
        item_type = get_simple_type(items, schemas, version) if isinstance(items, dict) else items.get("type", "?")
        return f"{item_type}[]"
    
    type_map = {"string": "str", "integer": "int", "boolean": "bool", "number": "num"}
    return type_map.get(prop_type, prop_type)

def generate_compact_docs(api_data: Dict[Any, Any], max_schema_props: int = 3) -> str:
    """Generate ultra-compact API documentation. Returns compact string or error string."""
    if not api_data:
        return f"{ERROR_PREFIX} API data is missing."
    version = detect_api_version(api_data)
    if not version:
        return f"{ERROR_PREFIX} Unknown or unsupported API specification version."
    
    output = []
    info = api_data.get("info", {})
    output.append(f"# {info.get('title', 'API')} v{info.get('version', '1.0.0')} (OAS {version})")

    paths, schemas, security_schemes_data = get_spec_components(api_data, version)

    if security_schemes_data:
        auth_types = set()
        for name, scheme in security_schemes_data.items():
            scheme_type = scheme.get("type", "unknown").lower()
            if scheme_type == "apikey": auth_types.add("ApiKey")
            elif scheme_type == "http": auth_types.add("HTTP")
            elif scheme_type == "basic": auth_types.add("Basic")
            elif scheme_type == "oauth2": auth_types.add("OAuth2")
            else: auth_types.add(scheme_type.capitalize())
        if auth_types: output.append(f"Auth: {', '.join(sorted(list(auth_types)))}")
    
    resource_groups = {}
    for path_str, path_item in paths.items():
        path_parts = [p for p in path_str.split('/') if p and not p.startswith('{')]
        resource = path_parts[1] if len(path_parts) >= 2 else "root"
        if len(path_parts) > 3 and not path_parts[2].startswith('{'): resource = f"{path_parts[1]}.{path_parts[3]}"
        
        for method, op_details in path_item.items():
            if method.lower() not in ["get", "post", "put", "delete", "patch", "options", "head", "trace"]:
                continue
            
            if resource not in resource_groups: resource_groups[resource] = []
            resource_groups[resource].append({"method": method.upper(), "path": path_str, "details": op_details})

    output.append("\n## Endpoints")
    for resource, endpoints in sorted(resource_groups.items()):
        output.append(f"\n**{resource}** ({len(endpoints)})")
        for ep in endpoints:
            method, path_str, details = ep["method"], ep["path"], ep["details"]
            
            s_path = path_str.replace("/api/", "/").replace("/{slug}", "/:s").replace("/{id}", "/:id")
            s_path = s_path.replace("/{username}", "/:u").replace("/{comment_id}", "/:c")
            line_parts = [f"{method} {s_path}"]

            if details.get("security") or (version == "2.0" and api_data.get("security")):
                line_parts.append("🔒")
            
            io_info = []
            req_body_schema = None
            if version == "2.0":
                body_param = next((p for p in details.get("parameters", []) if p.get("in") == "body"), None)
                if body_param: req_body_schema = body_param.get("schema")
            elif version in ["3.0", "3.1"]:
                rb = details.get("requestBody")
                if rb and isinstance(rb.get("content"), dict):
                     json_content = rb["content"].get("application/json") or rb["content"].get("*/*")
                     if json_content: req_body_schema = json_content.get("schema")
            
            if req_body_schema:
                req_type = extract_compact_type(req_body_schema, schemas, version)
                io_info.append(f"←{req_type[:17] + '...' if len(req_type) > 20 else req_type}")

            responses = details.get("responses", {})
            success_code = next((c for c in responses if c.startswith("2")), None)
            if success_code:
                resp_details = responses[success_code]
                resp_schema = None
                if version == "2.0":
                    resp_schema = resp_details.get("schema")
                elif version in ["3.0", "3.1"]:
                    if isinstance(resp_details.get("content"), dict):
                        json_content = resp_details["content"].get("application/json") or resp_details["content"].get("*/*")
                        if json_content: resp_schema = json_content.get("schema")
                
                if resp_schema:
                    resp_type = extract_compact_type(resp_schema, schemas, version)
                    io_info.append(f"→{resp_type[:17] + '...' if len(resp_type) > 20 else resp_type}")
            
            params_list = details.get("parameters", [])
            if version == "2.0" and isinstance(path_item.get("parameters"), list):
                params_list.extend(path_item["parameters"])

            if params_list:
                path_p_count = sum(1 for p in params_list if p.get("in") == "path")
                query_p_count = sum(1 for p in params_list if p.get("in") == "query")
                param_counts = []
                if path_p_count: param_counts.append(f"P{path_p_count}")
                if query_p_count: param_counts.append(f"Q{query_p_count}")
                if param_counts: io_info.append(f"({','.join(param_counts)})")
            
            if io_info: line_parts.extend(io_info)
            output.append(" ".join(line_parts))

    if schemas:
        output.append("\n## Types")
        used_schemas_names = set()
        schema_names_to_display = sorted(list(schemas.keys()))[:20]

        for schema_name in schema_names_to_display:
            schema_def = schemas[schema_name]
            properties = schema_def.get("properties", {})
            required = schema_def.get("required", []) if isinstance(schema_def.get("required"), list) else []
            
            if properties:
                prop_details = []
                for prop_name, prop_def in list(properties.items())[:max_schema_props + 2]:
                    is_req = "*" if prop_name in required else ""
                    prop_type = get_simple_type(prop_def, schemas, version)
                    prop_details.append(f"{prop_name}{is_req}:{prop_type}")
                    if len(prop_details) >= max_schema_props: break
                
                if len(properties) > len(prop_details):
                    prop_details.append(f"...+{len(properties) - len(prop_details)}")
                output.append(f"{schema_name}: {{{', '.join(prop_details)}}}")
            elif schema_def.get("type"):
                 output.append(f"{schema_name}: {extract_compact_type(schema_def, schemas, version)}")


    total_endpoints = sum(len(v) for v in resource_groups.values())
    method_counts = {}
    for endpoints in resource_groups.values():
        for ep in endpoints:
            method_counts[ep["method"]] = method_counts.get(ep["method"], 0) + 1
    
    methods_summary = ','.join(f'{m[0]}{c}' for m,c in sorted(method_counts.items()))
    output.append(f"\n**{total_endpoints} endpoints, {len(schemas)} schemas** | Methods: {methods_summary}")
    output.append("🔒=auth ←=req →=resp Pn=path-params Qn=query-params *=required")
    return "\n".join(output)

def main():
    """Main function to generate compact API documentation."""
    if len(sys.argv) < 2:
        print("Usage: python compact_api_docs.py <api_url> [max_schema_props]")
        print("Output will be printed to STDOUT.")
        print("Example: python compact_api_docs.py http://localhost:8000/openapi.json")
        print("Example: python compact_api_docs.py https://petstore.swagger.io/v2/swagger.json 3")
        return
    
    api_url = sys.argv[1]
    max_props = int(sys.argv[2]) if len(sys.argv) > 2 else 3 
    
    api_data, error_msg = get_api_spec(api_url)
    
    if error_msg:
        print(error_msg, file=sys.stderr)
        return 

    if api_data: 
        compact_docs = generate_compact_docs(api_data, max_props)
        
        if compact_docs.startswith(ERROR_PREFIX):
            print(compact_docs, file=sys.stderr)
        else:
            print(compact_docs)
            
            char_count = len(compact_docs)
            paths_data = api_data.get("paths", {})
            total_ops_calc = 0
            for path_item in paths_data.values():
                if isinstance(path_item, dict):
                    for method in path_item.keys():
                        if method.lower() in ["get", "post", "put", "delete", "patch", "options", "head", "trace"]:
                            total_ops_calc += 1
            print(f"✅ Successfully generated compact docs for {total_ops_calc} operations ({char_count:,} chars). Output to STDOUT.", file=sys.stderr)

if __name__ == "__main__":
    main() 