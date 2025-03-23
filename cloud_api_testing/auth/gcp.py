"""
GCP authentication for cloud API testing.
"""
import logging
import time
import json
import requests
from typing import Dict, Any, Optional

class GcpAuth:
    """Authentication handler for Google Cloud Platform API requests."""
    
    def __init__(
        self, 
        service_account_key: Dict[str, Any] = None,
        service_account_file: str = None,
        scopes: Optional[list] = None
    ):
        """
        Initialize GCP authentication.
        
        Args:
            service_account_key: Service account key as dictionary
            service_account_file: Path to service account key file
            scopes: OAuth scopes to request (default: cloud-platform)
        """
        self.logger = logging.getLogger(__name__)
        
        if service_account_key:
            self.service_account_key = service_account_key
        elif service_account_file:
            with open(service_account_file, 'r') as f:
                self.service_account_key = json.load(f)
        else:
            raise ValueError("Either service_account_key or service_account_file must be provided")
        
        self.scopes = scopes or ['https://www.googleapis.com/auth/cloud-platform']
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
        Get authentication headers for GCP request.
        
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
        
        self.logger.debug(f"Generated GCP auth headers for {method} {url}")
        return headers
    
    def _get_access_token(self) -> str:
        """
        Get GCP access token.
        
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
        self.logger.info("Acquiring new GCP access token")
        
        try:
            # Prepare JWT claim set
            iat = int(time.time())
            exp = iat + 3600  # 1 hour expiry
            
            claim_set = {
                'iss': self.service_account_key['client_email'],
                'scope': ' '.join(self.scopes),
                'aud': 'https://oauth2.googleapis.com/token',
                'exp': exp,
                'iat': iat
            }
            
            # Create JWT
            import jwt
            
            # Sign JWT with private key
            private_key = self.service_account_key['private_key']
            signed_jwt = jwt.encode(
                claim_set,
                private_key,
                algorithm='RS256'
            )
            
            # Exchange JWT for access token
            token_url = 'https://oauth2.googleapis.com/token'
            token_data = {
                'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                'assertion': signed_jwt
            }
            
            response = requests.post(token_url, data=token_data)
            response.raise_for_status()
            
            # Parse response
            token_response = response.json()
            self._token = token_response['access_token']
            self._token_expiry = current_time + token_response['expires_in']
            
            self.logger.info("Successfully acquired GCP access token")
            return self._token
        
        except Exception as e:
            self.logger.error(f"Failed to acquire GCP access token: {str(e)}")
            raise
