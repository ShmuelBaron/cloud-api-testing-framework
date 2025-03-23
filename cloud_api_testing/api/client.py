"""
API client for cloud service testing.
"""
import requests
import logging
import json
from typing import Dict, Any, Optional, Union

class ApiClient:
    """Client for making API requests to cloud services."""
    
    def __init__(self, base_url: str, auth=None, timeout: int = 30):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL for API requests
            auth: Authentication handler (optional)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.auth = auth
        self.timeout = timeout
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
    
    def send_request(
        self, 
        method: str, 
        endpoint: str, 
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> requests.Response:
        """
        Send an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (will be appended to base_url)
            headers: Request headers
            params: Query parameters
            data: Request body (for form data or plain text)
            json_data: Request body as JSON
            files: Files to upload
            timeout: Request timeout in seconds (overrides default)
            
        Returns:
            Response: HTTP response object
            
        Raises:
            requests.RequestException: If request fails
        """
        # Prepare request URL
        url = f"{self.base_url}{endpoint}"
        
        # Use default timeout if not specified
        if timeout is None:
            timeout = self.timeout
        
        # Prepare request headers
        request_headers = {}
        if headers:
            request_headers.update(headers)
        
        # Apply authentication if provided
        auth_headers = {}
        if self.auth:
            auth_headers = self.auth.get_auth_headers(method, url, headers, params, data, json_data)
            request_headers.update(auth_headers)
        
        # Log request details
        self.logger.info(f"Sending {method} request to {url}")
        self.logger.debug(f"Headers: {request_headers}")
        if params:
            self.logger.debug(f"Params: {params}")
        if data:
            self.logger.debug(f"Data: {data}")
        if json_data:
            self.logger.debug(f"JSON: {json_data}")
        if files:
            self.logger.debug(f"Files: {list(files.keys())}")
        
        try:
            # Send request
            response = self.session.request(
                method=method.upper(),
                url=url,
                headers=request_headers,
                params=params,
                data=data,
                json=json_data,
                files=files,
                timeout=timeout
            )
            
            # Log response details
            self.logger.info(f"Received response: {response.status_code}")
            self.logger.debug(f"Response headers: {response.headers}")
            
            # Try to log response body if not too large
            try:
                if len(response.content) < 10000:  # Only log if less than 10KB
                    if 'application/json' in response.headers.get('Content-Type', ''):
                        self.logger.debug(f"Response JSON: {response.json()}")
                    else:
                        self.logger.debug(f"Response text: {response.text}")
            except Exception as e:
                self.logger.debug(f"Could not log response content: {str(e)}")
            
            return response
        
        except requests.RequestException as e:
            self.logger.error(f"Request failed: {str(e)}")
            raise
    
    def get(self, endpoint: str, **kwargs) -> requests.Response:
        """
        Send a GET request.
        
        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments for send_request
            
        Returns:
            Response: HTTP response object
        """
        return self.send_request('GET', endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> requests.Response:
        """
        Send a POST request.
        
        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments for send_request
            
        Returns:
            Response: HTTP response object
        """
        return self.send_request('POST', endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs) -> requests.Response:
        """
        Send a PUT request.
        
        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments for send_request
            
        Returns:
            Response: HTTP response object
        """
        return self.send_request('PUT', endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """
        Send a DELETE request.
        
        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments for send_request
            
        Returns:
            Response: HTTP response object
        """
        return self.send_request('DELETE', endpoint, **kwargs)
    
    def patch(self, endpoint: str, **kwargs) -> requests.Response:
        """
        Send a PATCH request.
        
        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments for send_request
            
        Returns:
            Response: HTTP response object
        """
        return self.send_request('PATCH', endpoint, **kwargs)
    
    def head(self, endpoint: str, **kwargs) -> requests.Response:
        """
        Send a HEAD request.
        
        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments for send_request
            
        Returns:
            Response: HTTP response object
        """
        return self.send_request('HEAD', endpoint, **kwargs)
    
    def options(self, endpoint: str, **kwargs) -> requests.Response:
        """
        Send an OPTIONS request.
        
        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments for send_request
            
        Returns:
            Response: HTTP response object
        """
        return self.send_request('OPTIONS', endpoint, **kwargs)
    
    def close(self):
        """Close the session."""
        self.session.close()
        self.logger.info("API client session closed")
