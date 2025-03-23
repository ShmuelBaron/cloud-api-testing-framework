"""
Azure authentication for cloud API testing.
"""
import logging
import time
import requests
from typing import Dict, Any, Optional

class AzureAuth:
    """Authentication handler for Azure API requests."""
    
    def __init__(
        self, 
        tenant_id: str, 
        client_id: str, 
        client_secret: str, 
        resource: Optional[str] = None
    ):
        """
        Initialize Azure authentication.
        
        Args:
            tenant_id: Azure AD tenant ID
            client_id: Azure AD client ID (application ID)
            client_secret: Azure AD client secret
            resource: Resource to access (default: Azure Management API)
        """
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.resource = resource or 'https://management.azure.com/'
        self.logger = logging.getLogger(__name__)
        self._token = None
        self._token_expiry = 0
    
    def get_auth_headers(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Get authentication headers for Azure request.
        
        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            params: Query parameters
            data: Request body
            json_data: Request body as JSON
            
        Returns:
            Dict: Authentication headers
        """
        # Create a copy of headers to avoid modifying the original
        headers = headers.copy() if headers else {}
        
        # Get access token
        token = self._get_access_token()
        
        # Add authorization header
        headers['Authorization'] = f"Bearer {token}"
        
        self.logger.debug(f"Generated Azure auth headers for {method} {url}")
        return headers
    
    def _get_access_token(self) -> str:
        """
        Get Azure AD access token.
        
        Returns:
            str: Access token
            
        Raises:
            Exception: If token acquisition fails
        """
        # Check if we have a valid token
        current_time = time.time()
        if self._token and current_time < self._token_expiry - 60:  # 60 seconds buffer
            return self._token
        
        # Token is expired or not acquired yet, get a new one
        self.logger.info("Acquiring new Azure access token")
        
        # Prepare token request
        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/token"
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'resource': self.resource
        }
        
        try:
            # Send token request
            response = requests.post(token_url, data=token_data)
            response.raise_for_status()
            
            # Parse response
            token_response = response.json()
            self._token = token_response['access_token']
            self._token_expiry = current_time + token_response['expires_in']
            
            self.logger.info("Successfully acquired Azure access token")
            return self._token
        
        except Exception as e:
            self.logger.error(f"Failed to acquire Azure access token: {str(e)}")
            raise
