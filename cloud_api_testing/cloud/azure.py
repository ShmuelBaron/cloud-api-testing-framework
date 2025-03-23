"""
Azure cloud service client for API testing.
"""
import logging
from typing import Dict, Any, Optional, List, Union

from cloud_api_testing.api.client import ApiClient
from cloud_api_testing.auth.azure import AzureAuth

class AzureClient:
    """Client for testing Azure cloud services."""
    
    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        client_secret: str,
        subscription_id: str = None
    ):
        """
        Initialize the Azure client.
        
        Args:
            tenant_id: Azure AD tenant ID
            client_id: Azure AD client ID (application ID)
            client_secret: Azure AD client secret
            subscription_id: Azure subscription ID (optional)
        """
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.subscription_id = subscription_id
        self.logger = logging.getLogger(__name__)
        self.clients = {}
    
    def get_management_client(self) -> ApiClient:
        """
        Get API client for Azure Resource Manager.
        
        Returns:
            ApiClient: API client for Azure Resource Manager
        """
        # Check if client already exists
        if 'management' in self.clients:
            return self.clients['management']
        
        # Create authentication handler
        auth = AzureAuth(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret,
            resource='https://management.azure.com/'
        )
        
        # Create API client
        client = ApiClient(base_url='https://management.azure.com', auth=auth)
        
        # Cache client
        self.clients['management'] = client
        
        self.logger.info("Created Azure Management API client")
        return client
    
    def get_graph_client(self) -> ApiClient:
        """
        Get API client for Microsoft Graph API.
        
        Returns:
            ApiClient: API client for Microsoft Graph API
        """
        # Check if client already exists
        if 'graph' in self.clients:
            return self.clients['graph']
        
        # Create authentication handler
        auth = AzureAuth(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret,
            resource='https://graph.microsoft.com'
        )
        
        # Create API client
        client = ApiClient(base_url='https://graph.microsoft.com/v1.0', auth=auth)
        
        # Cache client
        self.clients['graph'] = client
        
        self.logger.info("Created Microsoft Graph API client")
        return client
    
    def list_resource_groups(self) -> Dict[str, Any]:
        """
        List Azure resource groups.
        
        Returns:
            Dict: Response data
        """
        if not self.subscription_id:
            return {
                'success': False,
                'error': "Subscription ID is required for this operation"
            }
        
        client = self.get_management_client()
        response = client.get(f"/subscriptions/{self.subscription_id}/resourcegroups?api-version=2021-04-01")
        
        if response.status_code == 200:
            return {
                'success': True,
                'resource_groups': response.json.get('value', [])
            }
        else:
            return {
                'success': False,
                'error': f"Failed to list resource groups: {response.status_code}",
                'response': response.text
            }
    
    def list_virtual_machines(self, resource_group: str = None) -> Dict[str, Any]:
        """
        List Azure virtual machines.
        
        Args:
            resource_group: Resource group name (optional)
            
        Returns:
            Dict: Response data
        """
        if not self.subscription_id:
            return {
                'success': False,
                'error': "Subscription ID is required for this operation"
            }
        
        client = self.get_management_client()
        
        if resource_group:
            # List VMs in specific resource group
            endpoint = f"/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines?api-version=2022-03-01"
        else:
            # List VMs in subscription
            endpoint = f"/subscriptions/{self.subscription_id}/providers/Microsoft.Compute/virtualMachines?api-version=2022-03-01"
        
        response = client.get(endpoint)
        
        if response.status_code == 200:
            return {
                'success': True,
                'virtual_machines': response.json.get('value', [])
            }
        else:
            return {
                'success': False,
                'error': f"Failed to list virtual machines: {response.status_code}",
                'response': response.text
            }
    
    def list_storage_accounts(self, resource_group: str = None) -> Dict[str, Any]:
        """
        List Azure storage accounts.
        
        Args:
            resource_group: Resource group name (optional)
            
        Returns:
            Dict: Response data
        """
        if not self.subscription_id:
            return {
                'success': False,
                'error': "Subscription ID is required for this operation"
            }
        
        client = self.get_management_client()
        
        if resource_group:
            # List storage accounts in specific resource group
            endpoint = f"/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Storage/storageAccounts?api-version=2021-09-01"
        else:
            # List storage accounts in subscription
            endpoint = f"/subscriptions/{self.subscription_id}/providers/Microsoft.Storage/storageAccounts?api-version=2021-09-01"
        
        response = client.get(endpoint)
        
        if response.status_code == 200:
            return {
                'success': True,
                'storage_accounts': response.json.get('value', [])
            }
        else:
            return {
                'success': False,
                'error': f"Failed to list storage accounts: {response.status_code}",
                'response': response.text
            }
    
    def list_users(self) -> Dict[str, Any]:
        """
        List Azure AD users.
        
        Returns:
            Dict: Response data
        """
        client = self.get_graph_client()
        response = client.get("/users")
        
        if response.status_code == 200:
            return {
                'success': True,
                'users': response.json.get('value', [])
            }
        else:
            return {
                'success': False,
                'error': f"Failed to list users: {response.status_code}",
                'response': response.text
            }
    
    def close(self):
        """Close all API clients."""
        for service, client in self.clients.items():
            client.close()
            self.logger.info(f"Closed Azure client for {service}")
        
        self.clients = {}
