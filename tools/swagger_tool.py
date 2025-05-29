import requests
import json


def get_swagger(url: str) -> str:
    """
    Function to get the swagger/OpenAPI specification from the given URL
    Args:
        url: str - The URL to fetch the swagger/OpenAPI spec from
    Returns:
        str: The swagger content as a formatted JSON string
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Try to parse as JSON to ensure it's valid
        swagger_data = response.json()
        
        # Return formatted JSON string
        return json.dumps(swagger_data, indent=2)
    except requests.exceptions.RequestException as e:
        return f"Error fetching swagger from {url}: {str(e)}"
    except json.JSONDecodeError as e:
        return f"Error parsing JSON from {url}: {str(e)}"


if __name__ == "__main__":
    print(get_swagger("http://localhost:8000/openapi.json"))





