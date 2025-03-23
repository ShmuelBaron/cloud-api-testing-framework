"""
GCP cloud service client for API testing.
"""
import logging
from typing import Dict, Any, Optional, List, Union

from cloud_api_testing.api.client import ApiClient
from cloud_api_testing.auth.gcp import GcpAuth

class GcpClient:
    """Client for testing Google Cloud Platform services."""
    
    def __init__(
        self,
        service_account_key: Dict[str, Any] = None,
        service_account_file: str = None,
        project_id: str = None
    ):
        """
        Initialize the GCP client.
        
        Args:
            service_account_key: Service account key as dictionary
            service_account_file: Path to service account key file
            project_id: GCP project ID (optional, will be extracted from service account if not provided)
        """
        self.service_account_key = service_account_key
        self.service_account_file = service_account_file
        
        # Extract project ID from service account if not provided
        if project_id:
            self.project_id = project_id
        elif service_account_key and 'project_id' in service_account_key:
            self.project_id = service_account_key['project_id']
        else:
            self.project_id = None
            
        self.logger = logging.getLogger(__name__)
        self.clients = {}
    
    def get_client(self, service: str, version: str = 'v1') -> ApiClient:
        """
        Get API client for specific GCP service.
        
        Args:
            service: GCP service name (e.g., 'compute', 'storage', 'cloudfunctions')
            version: API version (default: 'v1')
            
        Returns:
            ApiClient: API client for the service
        """
        # Check if client already exists
        client_key = f"{service}_{version}"
        if client_key in self.clients:
            return self.clients[client_key]
        
        # Create authentication handler
        auth = GcpAuth(
            service_account_key=self.service_account_key,
            service_account_file=self.service_account_file
        )
        
        # Create base URL for service
        base_url = f"https://{service}.googleapis.com/{version}"
        
        # Create API client
        client = ApiClient(base_url=base_url, auth=auth)
        
        # Cache client
        self.clients[client_key] = client
        
        self.logger.info(f"Created GCP client for {service} {version}")
        return client
    
    def list_compute_instances(self, zone: str = None) -> Dict[str, Any]:
        """
        List Compute Engine instances.
        
        Args:
            zone: Compute zone (optional)
            
        Returns:
            Dict: Response data
        """
        if not self.project_id:
            return {
                'success': False,
                'error': "Project ID is required for this operation"
            }
        
        client = self.get_client('compute')
        
        if zone:
            # List instances in specific zone
            endpoint = f"/projects/{self.project_id}/zones/{zone}/instances"
        else:
            # List instances in all zones (aggregated)
            endpoint = f"/projects/{self.project_id}/aggregated/instances"
        
        response = client.get(endpoint)
        
        if response.status_code == 200:
            return {
                'success': True,
                'instances': response.json.get('items', [])
            }
        else:
            return {
                'success': False,
                'error': f"Failed to list instances: {response.status_code}",
                'response': response.text
            }
    
    def list_storage_buckets(self) -> Dict[str, Any]:
        """
        List Cloud Storage buckets.
        
        Returns:
            Dict: Response data
        """
        if not self.project_id:
            return {
                'success': False,
                'error': "Project ID is required for this operation"
            }
        
        client = self.get_client('storage')
        response = client.get(f"/b?project={self.project_id}")
        
        if response.status_code == 200:
            return {
                'success': True,
                'buckets': response.json.get('items', [])
            }
        else:
            return {
                'success': False,
                'error': f"Failed to list buckets: {response.status_code}",
                'response': response.text
            }
    
    def list_storage_objects(self, bucket: str, prefix: str = None) -> Dict[str, Any]:
        """
        List objects in Cloud Storage bucket.
        
        Args:
            bucket: Bucket name
            prefix: Object prefix (optional)
            
        Returns:
            Dict: Response data
        """
        client = self.get_client('storage')
        
        params = {}
        if prefix:
            params['prefix'] = prefix
        
        response = client.get(f"/b/{bucket}/o", params=params)
        
        if response.status_code == 200:
            return {
                'success': True,
                'objects': response.json.get('items', [])
            }
        else:
            return {
                'success': False,
                'error': f"Failed to list objects: {response.status_code}",
                'response': response.text
            }
    
    def list_cloud_functions(self, region: str = None) -> Dict[str, Any]:
        """
        List Cloud Functions.
        
        Args:
            region: Region (optional)
            
        Returns:
            Dict: Response data
        """
        if not self.project_id:
            return {
                'success': False,
                'error': "Project ID is required for this operation"
            }
        
        client = self.get_client('cloudfunctions')
        
        if region:
            # List functions in specific region
            endpoint = f"/projects/{self.project_id}/locations/{region}/functions"
        else:
            # List functions in all regions
            endpoint = f"/projects/{self.project_id}/locations/-/functions"
        
        response = client.get(endpoint)
        
        if response.status_code == 200:
            return {
                'success': True,
                'functions': response.json.get('functions', [])
            }
        else:
            return {
                'success': False,
                'error': f"Failed to list functions: {response.status_code}",
                'response': response.text
            }
    
    def close(self):
        """Close all API clients."""
        for service, client in self.clients.items():
            client.close()
            self.logger.info(f"Closed GCP client for {service}")
        
        self.clients = {}
