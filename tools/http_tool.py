import requests

def http_request(
    method: str,
    url: str,
    *,
    headers: dict = None,
    params: dict = None,
    data: dict = None,
    json: dict = None,
    files: dict = None,
    cookies: dict = None,
    timeout: int = 10,
    verify: bool = True,
    allow_redirects: bool = True,
    proxies: dict = None
):
    """
    Sends an HTTP request with full control over all common parameters.

    Args:
        method (str): HTTP method (e.g., 'GET', 'POST', 'PUT', 'DELETE').
        url (str): The URL to send the request to.
        headers (dict, optional): HTTP headers.
        params (dict, optional): URL query parameters.
        data (dict or str, optional): Form data or raw body.
        json (dict, optional): JSON body (overrides `data` if provided).
        files (dict, optional): Files to send in a multipart/form-data request.
        cookies (dict, optional): Cookies to send with the request.
        timeout (int, optional): Timeout for the request in seconds.
        verify (bool, optional): Whether to verify SSL certificates.
        allow_redirects (bool, optional): Follow redirects.
        proxies (dict, optional): Proxy servers to use for the request.

    Returns:
        tuple: (status_code: int, response_text: str), or (None, None) on failure.

    Example:
        >>> status, body = http_request(
        ...     method="POST",
        ...     url="https://example.com/api/login",
        ...     headers={"Content-Type": "application/json"},
        ...     json={"username": "admin", "password": "admin123"}
        ... )
        >>> print(status)
        >>> print(body)
    """
    print(f"\n🔥 HTTP_TOOL: Making {method.upper()} request to {url}")
    
    if headers:
        print(f"📝 Headers: {headers}")
    if params:
        print(f"🔗 Params: {params}")
    if data:
        print(f"📄 Data: {data}")
    if json:
        print(f"📋 JSON: {json}")
    if cookies:
        print(f"🍪 Cookies: {cookies}")
    
    if not isinstance(url, str) or not url.startswith(("http://", "https://")):
        error_msg = f"Invalid or missing URL: {url}"
        print(f"❌ {error_msg}")
        return None, None

    try:
        response = requests.request(
            method=method.upper(),
            url=url,
            headers=headers,
            params=params,
            data=data,
            json=json,
            files=files,
            cookies=cookies,
            timeout=timeout,
            verify=verify,
            allow_redirects=allow_redirects,
            proxies=proxies
        )
        
        print(f"✅ Response Status: {response.status_code}")
        print(f"📊 Response Length: {len(response.text)} characters")
        
        # Show first 200 characters of response for debugging
        if len(response.text) > 200:
            print(f"📖 Response Preview: {response.text[:200]}...")
        else:
            print(f"📖 Response Body: {response.text}")
        
        return response.status_code, response.text
    except requests.RequestException as e:
        error_msg = f"HTTP request failed: {e}"
        print(f"❌ {error_msg}")
        return None, None


if __name__ == "__main__":
    # Example: Simple GET request to a local endpoint
    status, body = http_request(
        method="GET",
        url="http://localhost:8000/openapi.json",
        headers={}
    )

    print(f"Status Code: {status}")
    print(f"Response Body:\n{body}")
