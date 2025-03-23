# Cloud API Testing Framework

A comprehensive framework for testing cloud service APIs across AWS, Azure, and Google Cloud Platform.

## Overview

This Cloud API Testing Framework provides a robust solution for testing APIs of major cloud service providers. Built with Python, it offers authentication handling, request/response modeling, validation utilities, and specialized clients for AWS, Azure, and GCP services.

## Features

- **Multi-Cloud Support**: Test APIs across AWS, Azure, and Google Cloud Platform
- **Authentication Handling**: Support for various authentication methods for each cloud provider
- **Request/Response Modeling**: Clean abstraction for API interactions
- **Validation Utilities**: JSON schema validation and response verification
- **Specialized Cloud Clients**: Purpose-built clients for common cloud services
- **Extensible Architecture**: Easily add support for additional cloud services
- **Comprehensive Logging**: Detailed logging for troubleshooting and audit trails
- **Error Handling**: Robust error handling and reporting

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/cloud-api-testing.git
cd cloud-api-testing

# Create and activate virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Project Structure

```
cloud_api_testing/
├── api/                  # API interaction components
│   ├── client.py         # Base API client
│   ├── request.py        # Request modeling
│   └── response.py       # Response handling
├── auth/                 # Authentication handlers
│   ├── aws.py            # AWS authentication
│   ├── azure.py          # Azure authentication
│   └── gcp.py            # GCP authentication
├── cloud/                # Cloud service clients
│   ├── aws.py            # AWS service client
│   ├── azure.py          # Azure service client
│   └── gcp.py            # GCP service client
├── validation/           # Validation utilities
│   ├── json_schema.py    # JSON schema validation
│   └── validators.py     # Response validators
├── config/               # Configuration files
├── utils/                # Utility functions
├── tests/                # Test cases
├── examples/             # Example usage
└── schemas/              # JSON schemas for validation
```

## Usage

### AWS API Testing Example

```python
from cloud_api_testing.cloud.aws import AwsClient
from cloud_api_testing.validation.validators import ResponseValidator

# Initialize AWS client
aws_client = AwsClient(
    access_key="YOUR_ACCESS_KEY",
    secret_key="YOUR_SECRET_KEY",
    region="us-west-2"
)

# List S3 buckets
result = aws_client.list_s3_buckets()

# Validate response
validator = ResponseValidator()
validation_result = validator.validate(
    result,
    {
        "success": True,
        "buckets": lambda x: isinstance(x, list)
    }
)

print(f"Validation passed: {validation_result.passed}")
if not validation_result.passed:
    print(f"Errors: {validation_result.errors}")
```

### Azure API Testing Example

```python
from cloud_api_testing.cloud.azure import AzureClient

# Initialize Azure client
azure_client = AzureClient(
    tenant_id="YOUR_TENANT_ID",
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    subscription_id="YOUR_SUBSCRIPTION_ID"
)

# List resource groups
result = azure_client.list_resource_groups()

# Process results
if result["success"]:
    print(f"Found {len(result['resource_groups'])} resource groups:")
    for group in result["resource_groups"]:
        print(f"- {group['name']} ({group['location']})")
else:
    print(f"Error: {result['error']}")
```

### GCP API Testing Example

```python
from cloud_api_testing.cloud.gcp import GcpClient
import json

# Initialize GCP client with service account key file
gcp_client = GcpClient(
    service_account_file="path/to/service-account-key.json"
)

# List storage buckets
result = gcp_client.list_storage_buckets()

# Output results as JSON
print(json.dumps(result, indent=2))
```

### Custom API Request Example

```python
from cloud_api_testing.api.client import ApiClient
from cloud_api_testing.auth.aws import AwsAuth

# Create authentication handler
auth = AwsAuth(
    access_key="YOUR_ACCESS_KEY",
    secret_key="YOUR_SECRET_KEY",
    region="us-west-2",
    service="ec2"
)

# Create API client
client = ApiClient(
    base_url="https://ec2.us-west-2.amazonaws.com",
    auth=auth
)

# Make API request
response = client.get(
    "/",
    params={
        "Action": "DescribeInstances",
        "Version": "2016-11-15"
    }
)

# Process response
if response.status_code == 200:
    print("Request successful")
    # Parse XML response
    # ...
else:
    print(f"Request failed: {response.status_code}")
    print(response.text)
```

## Configuration

The framework supports configuration through JSON files located in the `config` directory.

Example configuration file (`config/aws.json`):

```json
{
  "aws": {
    "region": "us-west-2",
    "credentials": {
      "profile": "default"
    },
    "retry": {
      "max_attempts": 3,
      "mode": "standard"
    }
  }
}
```

## Advanced Features

### JSON Schema Validation

```python
from cloud_api_testing.validation.json_schema import JsonSchemaValidator

# Define schema
schema = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "instances": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "type": {"type": "string"},
                    "state": {"type": "string"}
                },
                "required": ["id", "type", "state"]
            }
        }
    },
    "required": ["success", "instances"]
}

# Validate response against schema
validator = JsonSchemaValidator(schema)
is_valid, errors = validator.validate(response_data)

if not is_valid:
    print(f"Validation errors: {errors}")
```

### Custom Authentication

```python
from cloud_api_testing.api.client import ApiClient
from cloud_api_testing.auth.base import BaseAuth

class CustomAuth(BaseAuth):
    def __init__(self, api_key):
        self.api_key = api_key
    
    def authenticate(self, request):
        request.headers["X-API-Key"] = self.api_key
        return request

# Use custom authentication
auth = CustomAuth("your-api-key")
client = ApiClient(base_url="https://api.example.com", auth=auth)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
