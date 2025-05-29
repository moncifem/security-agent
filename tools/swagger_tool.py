import requests


def get_swagger(url: str):
    """
    Function to get the swagger from the given url
    Args:
        url: str
    Returns:
        str: The swagger content
    """
    return requests.get(url).content


if __name__ == "__main__":
    print(get_swagger("http://localhost:8000/openapi.json"))





