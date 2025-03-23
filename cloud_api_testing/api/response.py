"""
API response model for cloud service testing.
"""
from typing import Dict, Any, Optional, Union
import json
import requests

class Response:
    """Model representing an API response."""
    
    def __init__(
        self,
        status_code: int,
        headers: Dict[str, str],
        content: bytes,
        elapsed_time: float,
        request_info: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the response model.
        
        Args:
            status_code: HTTP status code
            headers: Response headers
            content: Response content as bytes
            elapsed_time: Request-response time in seconds
            request_info: Information about the request that generated this response
        """
        self.status_code = status_code
        self.headers = headers
        self.content = content
        self.elapsed_time = elapsed_time
        self.request_info = request_info or {}
        self._json = None
        self._text = None
    
    @property
    def text(self) -> str:
        """
        Get response content as text.
        
        Returns:
            str: Response text
        """
        if self._text is None:
            self._text = self.content.decode('utf-8', errors='replace')
        return self._text
    
    @property
    def json(self) -> Any:
        """
        Get response content as JSON.
        
        Returns:
            Any: Parsed JSON data
            
        Raises:
            ValueError: If response is not valid JSON
        """
        if self._json is None:
            try:
                self._json = json.loads(self.text)
            except json.JSONDecodeError as e:
                raise ValueError(f"Response is not valid JSON: {str(e)}")
        return self._json
    
    def is_success(self) -> bool:
        """
        Check if response indicates success (2xx status code).
        
        Returns:
            bool: True if successful, False otherwise
        """
        return 200 <= self.status_code < 300
    
    def is_redirect(self) -> bool:
        """
        Check if response is a redirect (3xx status code).
        
        Returns:
            bool: True if redirect, False otherwise
        """
        return 300 <= self.status_code < 400
    
    def is_client_error(self) -> bool:
        """
        Check if response indicates client error (4xx status code).
        
        Returns:
            bool: True if client error, False otherwise
        """
        return 400 <= self.status_code < 500
    
    def is_server_error(self) -> bool:
        """
        Check if response indicates server error (5xx status code).
        
        Returns:
            bool: True if server error, False otherwise
        """
        return 500 <= self.status_code < 600
    
    def get_header(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a specific header value.
        
        Args:
            name: Header name (case-insensitive)
            default: Default value if header not found
            
        Returns:
            str or None: Header value or default
        """
        for key, value in self.headers.items():
            if key.lower() == name.lower():
                return value
        return default
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert response to dictionary.
        
        Returns:
            Dict: Response as dictionary
        """
        response_dict = {
            'status_code': self.status_code,
            'headers': dict(self.headers),
            'elapsed_time': self.elapsed_time
        }
        
        # Try to include content as text or JSON
        try:
            if 'application/json' in self.headers.get('Content-Type', ''):
                response_dict['json'] = self.json
            else:
                response_dict['text'] = self.text
        except Exception:
            response_dict['content_length'] = len(self.content)
        
        if self.request_info:
            response_dict['request'] = self.request_info
        
        return response_dict
    
    def __str__(self) -> str:
        """
        Get string representation of the response.
        
        Returns:
            str: Response as string
        """
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_requests_response(cls, response: requests.Response) -> 'Response':
        """
        Create response from requests.Response object.
        
        Args:
            response: requests.Response object
            
        Returns:
            Response: Response instance
        """
        request_info = {
            'method': response.request.method,
            'url': response.request.url,
            'headers': dict(response.request.headers)
        }
        
        return cls(
            status_code=response.status_code,
            headers=dict(response.headers),
            content=response.content,
            elapsed_time=response.elapsed.total_seconds(),
            request_info=request_info
        )
