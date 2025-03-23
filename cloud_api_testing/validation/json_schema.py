"""
JSON schema validation for API responses.
"""
import json
import jsonschema
import logging
from typing import Dict, Any, Optional, Union

class JsonSchemaValidator:
    """Validator for JSON responses using JSON Schema."""
    
    def __init__(self, schema_dir: Optional[str] = None):
        """
        Initialize the JSON schema validator.
        
        Args:
            schema_dir: Directory containing schema files (optional)
        """
        self.schema_dir = schema_dir
        self.logger = logging.getLogger(__name__)
        self.schema_cache = {}
    
    def validate(self, data: Dict[str, Any], schema: Union[Dict[str, Any], str]) -> Dict[str, Any]:
        """
        Validate data against JSON schema.
        
        Args:
            data: Data to validate
            schema: JSON schema as dictionary or path to schema file
            
        Returns:
            Dict: Validation result with 'valid' and 'errors' keys
            
        Raises:
            FileNotFoundError: If schema file is not found
            jsonschema.exceptions.SchemaError: If schema is invalid
        """
        # Load schema if it's a string (file path)
        if isinstance(schema, str):
            schema = self._load_schema(schema)
        
        result = {
            'valid': True,
            'errors': []
        }
        
        try:
            jsonschema.validate(instance=data, schema=schema)
            self.logger.info("JSON validation successful")
        except jsonschema.exceptions.ValidationError as e:
            result['valid'] = False
            result['errors'].append({
                'message': str(e),
                'path': '.'.join(str(p) for p in e.path) if e.path else '',
                'schema_path': '.'.join(str(p) for p in e.schema_path) if e.schema_path else ''
            })
            self.logger.warning(f"JSON validation failed: {str(e)}")
        
        return result
    
    def _load_schema(self, schema_path: str) -> Dict[str, Any]:
        """
        Load JSON schema from file.
        
        Args:
            schema_path: Path to schema file
            
        Returns:
            Dict: JSON schema
            
        Raises:
            FileNotFoundError: If schema file is not found
            json.JSONDecodeError: If schema file is not valid JSON
        """
        # Check if schema is already cached
        if schema_path in self.schema_cache:
            return self.schema_cache[schema_path]
        
        # If schema_path doesn't have .json extension and schema_dir is provided,
        # try to load from schema_dir
        if self.schema_dir and not schema_path.endswith('.json'):
            import os
            full_path = os.path.join(self.schema_dir, f"{schema_path}.json")
        else:
            full_path = schema_path
        
        try:
            with open(full_path, 'r') as f:
                schema = json.load(f)
                self.schema_cache[schema_path] = schema
                self.logger.info(f"Loaded JSON schema from {full_path}")
                return schema
        except FileNotFoundError:
            self.logger.error(f"Schema file not found: {full_path}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON schema file: {full_path} - {str(e)}")
            raise
