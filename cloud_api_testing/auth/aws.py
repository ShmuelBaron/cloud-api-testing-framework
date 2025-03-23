"""
AWS authentication for cloud API testing.
"""
import hmac
import hashlib
import datetime
import logging
from typing import Dict, Any, Optional

class AwsAuth:
    """Authentication handler for AWS API requests."""
    
    def __init__(self, access_key: str, secret_key: str, region: str = 'us-east-1', service: str = 's3'):
        """
        Initialize AWS authentication.
        
        Args:
            access_key: AWS access key ID
            secret_key: AWS secret access key
            region: AWS region (default: us-east-1)
            service: AWS service (default: s3)
        """
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.service = service
        self.logger = logging.getLogger(__name__)
    
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
        Get authentication headers for AWS request.
        
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
        
        # Get current timestamp
        now = datetime.datetime.utcnow()
        amz_date = now.strftime('%Y%m%dT%H%M%SZ')
        date_stamp = now.strftime('%Y%m%d')
        
        # Add required headers
        headers['X-Amz-Date'] = amz_date
        
        # Create canonical request
        canonical_uri = self._get_canonical_uri(url)
        canonical_querystring = self._get_canonical_querystring(params)
        canonical_headers = self._get_canonical_headers(headers)
        signed_headers = self._get_signed_headers(headers)
        
        # Create payload hash
        payload_hash = self._get_payload_hash(data, json_data)
        
        # Combine elements to create canonical request
        canonical_request = f"{method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
        
        # Create string to sign
        algorithm = 'AWS4-HMAC-SHA256'
        credential_scope = f"{date_stamp}/{self.region}/{self.service}/aws4_request"
        string_to_sign = f"{algorithm}\n{amz_date}\n{credential_scope}\n{self._hash_sha256(canonical_request)}"
        
        # Calculate signature
        signing_key = self._get_signature_key(self.secret_key, date_stamp, self.region, self.service)
        signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
        
        # Add authorization header
        auth_header = (
            f"{algorithm} "
            f"Credential={self.access_key}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, "
            f"Signature={signature}"
        )
        
        headers['Authorization'] = auth_header
        
        self.logger.debug(f"Generated AWS auth headers for {method} {url}")
        return headers
    
    def _hash_sha256(self, data: str) -> str:
        """
        Calculate SHA256 hash of string.
        
        Args:
            data: String to hash
            
        Returns:
            str: Hexadecimal hash
        """
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def _get_canonical_uri(self, url: str) -> str:
        """
        Get canonical URI from URL.
        
        Args:
            url: Request URL
            
        Returns:
            str: Canonical URI
        """
        # Extract path from URL
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        path = parsed_url.path
        
        # Use '/' if path is empty
        if not path:
            return '/'
        
        # Ensure path starts with '/'
        if not path.startswith('/'):
            path = '/' + path
        
        return path
    
    def _get_canonical_querystring(self, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Get canonical query string from parameters.
        
        Args:
            params: Query parameters
            
        Returns:
            str: Canonical query string
        """
        if not params:
            return ''
        
        # Sort parameters by key
        sorted_params = sorted(params.items())
        
        # URL encode parameters
        from urllib.parse import quote
        encoded_params = []
        for key, value in sorted_params:
            encoded_key = quote(str(key), safe='-_.~')
            encoded_value = quote(str(value), safe='-_.~')
            encoded_params.append(f"{encoded_key}={encoded_value}")
        
        return '&'.join(encoded_params)
    
    def _get_canonical_headers(self, headers: Dict[str, str]) -> str:
        """
        Get canonical headers string.
        
        Args:
            headers: Request headers
            
        Returns:
            str: Canonical headers string
        """
        # Convert header names to lowercase and sort by name
        canonical_headers = {}
        for key, value in headers.items():
            canonical_headers[key.lower()] = value.strip()
        
        # Create canonical headers string
        header_strings = []
        for key in sorted(canonical_headers.keys()):
            header_strings.append(f"{key}:{canonical_headers[key]}")
        
        return '\n'.join(header_strings) + '\n'
    
    def _get_signed_headers(self, headers: Dict[str, str]) -> str:
        """
        Get signed headers string.
        
        Args:
            headers: Request headers
            
        Returns:
            str: Signed headers string
        """
        # Convert header names to lowercase and sort by name
        header_names = [key.lower() for key in headers.keys()]
        return ';'.join(sorted(header_names))
    
    def _get_payload_hash(self, data: Optional[Any], json_data: Optional[Dict[str, Any]]) -> str:
        """
        Get hash of request payload.
        
        Args:
            data: Request body
            json_data: Request body as JSON
            
        Returns:
            str: Payload hash
        """
        import json
        
        if json_data is not None:
            payload = json.dumps(json_data)
        elif data is not None:
            payload = data if isinstance(data, str) else str(data)
        else:
            payload = ''
        
        return self._hash_sha256(payload)
    
    def _get_signature_key(self, key: str, date_stamp: str, region_name: str, service_name: str) -> bytes:
        """
        Get signature key for AWS Signature Version 4.
        
        Args:
            key: Secret access key
            date_stamp: Date in YYYYMMDD format
            region_name: AWS region
            service_name: AWS service
            
        Returns:
            bytes: Signature key
        """
        k_date = hmac.new(f'AWS4{key}'.encode('utf-8'), date_stamp.encode('utf-8'), hashlib.sha256).digest()
        k_region = hmac.new(k_date, region_name.encode('utf-8'), hashlib.sha256).digest()
        k_service = hmac.new(k_region, service_name.encode('utf-8'), hashlib.sha256).digest()
        k_signing = hmac.new(k_service, b'aws4_request', hashlib.sha256).digest()
        return k_signing
