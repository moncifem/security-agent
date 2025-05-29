import requests


def get_swagger(url: str):
    return requests.get(url).content


if __name__ == "__main__":
    print(get_swagger("http://localhost:8000/openapi.json"))





