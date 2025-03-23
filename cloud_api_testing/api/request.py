"""
API request model for cloud service testing.
"""
from typing import Dict, Any, Optional, Union
import json

class Request:
    """Model representing an API request."""
    
    def __init__(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        auth: Optional[Any] = None,
        timeout: Optional[int] = None
    ):
        """
        Initialize the request model.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            url: Request URL
            headers: Request headers
            params: Query parameters
            data: Request body (for form data or plain text)
            json_data: Request body as JSON
            files: Files to upload
            auth: Authentication information
            timeout: Request timeout in seconds
        """
        self.method = method.upper()
        self.url = url
        self.headers = headers or {}
        self.params = params or {}
        self.data = data
        self.json_data = json_data
        self.files = files
        self.auth = auth
        self.timeout = timeout
    
    def add_header(self, key: str, value: str) -> 'Request':
        """
        Add a header to the request.
        
        Args:
            key: Header name
            value: Header value
            
        Returns:
            Request: Self for method chaining
        """
        self.headers[key] = value
        return self
    
    def add_param(self, key: str, value: Any) -> 'Request':
        """
        Add a query parameter to the request.
        
        Args:
            key: Parameter name
            value: Parameter value
            
        Returns:
            Request: Self for method chaining
        """
        self.params[key] = value
        return self
    
    def set_json_data(self, data: Dict[str, Any]) -> 'Request':
        """
        Set JSON data for the request.
        
        Args:
            data: JSON data
            
        Returns:
            Request: Self for method chaining
        """
        self.json_data = data
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert request to dictionary.
        
        Returns:
            Dict: Request as dictionary
        """
        request_dict = {
            'method': self.method,
            'url': self.url
        }
        
        if self.headers:
            request_dict['headers'] = self.headers
        
        if self.params:
            request_dict['params'] = self.params
        
        if self.data:
            request_dict['data'] = self.data
        
        if self.json_data:
            request_dict['json'] = self.json_data
        
        if self.files:
            request_dict['files'] = {k: f"<file:{v}>" for k, v in self.files.items()}
        
        if self.auth:
            request_dict['auth'] = str(self.auth)
        
        if self.timeout:
            request_dict['timeout'] = self.timeout
        
        return request_dict
    
    def __str__(self) -> str:
        """
        Get string representation of the request.
        
        Returns:
            str: Request as string
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Request':
        """
        Create request from dictionary.
        
        Args:
            data: Dictionary with request data
            
        Returns:
            Request: Request instance
            
        Raises:
            ValueError: If required fields are missing
        """
        if 'method' not in data or 'url' not in data:
            raise ValueError("Method and URL are required")
        
        return cls(
            method=data['method'],
            url=data['url'],
            headers=data.get('headers'),
            params=data.get('params'),
            data=data.get('data'),
            json_data=data.get('json'),
            files=data.get('files'),
            auth=data.get('auth'),
            timeout=data.get('timeout')
        )
