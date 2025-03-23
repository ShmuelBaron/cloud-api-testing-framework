"""
AWS cloud service client for API testing.
"""
import logging
from typing import Dict, Any, Optional, List, Union

from cloud_api_testing.api.client import ApiClient
from cloud_api_testing.auth.aws import AwsAuth

class AwsClient:
    """Client for testing AWS cloud services."""
    
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        region: str = 'us-east-1',
        service: str = None
    ):
        """
        Initialize the AWS client.
        
        Args:
            access_key: AWS access key ID
            secret_key: AWS secret access key
            region: AWS region (default: us-east-1)
            service: AWS service (default: None, will be set per request)
        """
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.default_service = service
        self.logger = logging.getLogger(__name__)
        self.clients = {}
    
    def get_client(self, service: str) -> ApiClient:
        """
        Get API client for specific AWS service.
        
        Args:
            service: AWS service name (e.g., 's3', 'ec2', 'lambda')
            
        Returns:
            ApiClient: API client for the service
        """
        # Check if client already exists
        if service in self.clients:
            return self.clients[service]
        
        # Create base URL for service
        if service == 's3':
            base_url = f"https://s3.{self.region}.amazonaws.com"
        else:
            base_url = f"https://{service}.{self.region}.amazonaws.com"
        
        # Create authentication handler
        auth = AwsAuth(
            access_key=self.access_key,
            secret_key=self.secret_key,
            region=self.region,
            service=service
        )
        
        # Create API client
        client = ApiClient(base_url=base_url, auth=auth)
        
        # Cache client
        self.clients[service] = client
        
        self.logger.info(f"Created AWS client for {service} in {self.region}")
        return client
    
    def s3_list_buckets(self) -> Dict[str, Any]:
        """
        List S3 buckets.
        
        Returns:
            Dict: Response data
        """
        client = self.get_client('s3')
        response = client.get('/')
        
        if response.status_code == 200:
            return {
                'success': True,
                'buckets': response.json.get('Buckets', []),
                'owner': response.json.get('Owner', {})
            }
        else:
            return {
                'success': False,
                'error': f"Failed to list buckets: {response.status_code}",
                'response': response.text
            }
    
    def s3_list_objects(self, bucket: str, prefix: str = None) -> Dict[str, Any]:
        """
        List objects in S3 bucket.
        
        Args:
            bucket: Bucket name
            prefix: Object prefix (optional)
            
        Returns:
            Dict: Response data
        """
        client = self.get_client('s3')
        
        params = {}
        if prefix:
            params['prefix'] = prefix
        
        response = client.get(f"/{bucket}", params=params)
        
        if response.status_code == 200:
            return {
                'success': True,
                'objects': response.json.get('Contents', []),
                'common_prefixes': response.json.get('CommonPrefixes', [])
            }
        else:
            return {
                'success': False,
                'error': f"Failed to list objects: {response.status_code}",
                'response': response.text
            }
    
    def ec2_describe_instances(self, instance_ids: List[str] = None) -> Dict[str, Any]:
        """
        Describe EC2 instances.
        
        Args:
            instance_ids: List of instance IDs (optional)
            
        Returns:
            Dict: Response data
        """
        client = self.get_client('ec2')
        
        params = {
            'Action': 'DescribeInstances',
            'Version': '2016-11-15'
        }
        
        if instance_ids:
            for i, instance_id in enumerate(instance_ids):
                params[f'InstanceId.{i+1}'] = instance_id
        
        response = client.get('/', params=params)
        
        if response.status_code == 200:
            return {
                'success': True,
                'reservations': response.json.get('Reservations', [])
            }
        else:
            return {
                'success': False,
                'error': f"Failed to describe instances: {response.status_code}",
                'response': response.text
            }
    
    def lambda_list_functions(self) -> Dict[str, Any]:
        """
        List Lambda functions.
        
        Returns:
            Dict: Response data
        """
        client = self.get_client('lambda')
        
        response = client.get('/2015-03-31/functions/')
        
        if response.status_code == 200:
            return {
                'success': True,
                'functions': response.json.get('Functions', [])
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
            self.logger.info(f"Closed AWS client for {service}")
        
        self.clients = {}
