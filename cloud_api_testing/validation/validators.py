"""
Validators for API testing.
"""
import re
import logging
from typing import Dict, Any, Optional, List, Union, Callable

class Validators:
    """Collection of validators for API responses."""
    
    def __init__(self):
        """Initialize the validators."""
        self.logger = logging.getLogger(__name__)
    
    def validate_status_code(self, response, expected_status: Union[int, List[int]]) -> Dict[str, Any]:
        """
        Validate response status code.
        
        Args:
            response: Response object
            expected_status: Expected status code or list of valid status codes
            
        Returns:
            Dict: Validation result with 'valid' and 'message' keys
        """
        if isinstance(expected_status, int):
            expected_status = [expected_status]
        
        actual_status = response.status_code
        is_valid = actual_status in expected_status
        
        result = {
            'valid': is_valid,
            'actual': actual_status,
            'expected': expected_status
        }
        
        if is_valid:
            result['message'] = f"Status code {actual_status} matches expected {expected_status}"
            self.logger.info(result['message'])
        else:
            result['message'] = f"Status code {actual_status} does not match expected {expected_status}"
            self.logger.warning(result['message'])
        
        return result
    
    def validate_header(self, response, header_name: str, expected_value: Optional[str] = None, 
                       pattern: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate response header.
        
        Args:
            response: Response object
            header_name: Header name to validate
            expected_value: Expected header value (optional)
            pattern: Regex pattern to match header value (optional)
            
        Returns:
            Dict: Validation result with 'valid' and 'message' keys
        """
        header_value = response.get_header(header_name)
        
        result = {
            'valid': False,
            'header_name': header_name,
            'actual': header_value
        }
        
        # Check if header exists
        if header_value is None:
            result['message'] = f"Header '{header_name}' not found in response"
            self.logger.warning(result['message'])
            return result
        
        # If expected value is provided, check exact match
        if expected_value is not None:
            result['expected'] = expected_value
            result['valid'] = header_value == expected_value
            
            if result['valid']:
                result['message'] = f"Header '{header_name}' value '{header_value}' matches expected '{expected_value}'"
                self.logger.info(result['message'])
            else:
                result['message'] = f"Header '{header_name}' value '{header_value}' does not match expected '{expected_value}'"
                self.logger.warning(result['message'])
            
            return result
        
        # If pattern is provided, check regex match
        if pattern is not None:
            result['pattern'] = pattern
            result['valid'] = bool(re.match(pattern, header_value))
            
            if result['valid']:
                result['message'] = f"Header '{header_name}' value '{header_value}' matches pattern '{pattern}'"
                self.logger.info(result['message'])
            else:
                result['message'] = f"Header '{header_name}' value '{header_value}' does not match pattern '{pattern}'"
                self.logger.warning(result['message'])
            
            return result
        
        # If neither expected value nor pattern is provided, just check existence
        result['valid'] = True
        result['message'] = f"Header '{header_name}' exists in response"
        self.logger.info(result['message'])
        
        return result
    
    def validate_json_path(self, response, json_path: str, expected_value: Optional[Any] = None,
                          validator: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Validate value at JSON path in response.
        
        Args:
            response: Response object
            json_path: JSONPath expression
            expected_value: Expected value at path (optional)
            validator: Custom validator function (optional)
            
        Returns:
            Dict: Validation result with 'valid' and 'message' keys
        """
        try:
            # Import jsonpath-ng
            from jsonpath_ng import parse
            
            # Parse JSON path expression
            jsonpath_expr = parse(json_path)
            
            # Find matches in response JSON
            matches = jsonpath_expr.find(response.json)
            
            result = {
                'valid': False,
                'json_path': json_path
            }
            
            # Check if path exists
            if not matches:
                result['message'] = f"JSON path '{json_path}' not found in response"
                self.logger.warning(result['message'])
                return result
            
            # Get the first match value
            actual_value = matches[0].value
            result['actual'] = actual_value
            
            # If expected value is provided, check exact match
            if expected_value is not None:
                result['expected'] = expected_value
                result['valid'] = actual_value == expected_value
                
                if result['valid']:
                    result['message'] = f"Value at '{json_path}' matches expected '{expected_value}'"
                    self.logger.info(result['message'])
                else:
                    result['message'] = f"Value at '{json_path}' is '{actual_value}', does not match expected '{expected_value}'"
                    self.logger.warning(result['message'])
                
                return result
            
            # If validator function is provided, use it
            if validator is not None:
                result['valid'] = validator(actual_value)
                
                if result['valid']:
                    result['message'] = f"Value at '{json_path}' passes custom validation"
                    self.logger.info(result['message'])
                else:
                    result['message'] = f"Value at '{json_path}' fails custom validation"
                    self.logger.warning(result['message'])
                
                return result
            
            # If neither expected value nor validator is provided, just check existence
            result['valid'] = True
            result['message'] = f"JSON path '{json_path}' exists in response"
            self.logger.info(result['message'])
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error validating JSON path: {str(e)}")
            return {
                'valid': False,
                'json_path': json_path,
                'message': f"Error validating JSON path: {str(e)}"
            }
    
    def validate_response_time(self, response, max_time: float) -> Dict[str, Any]:
        """
        Validate response time.
        
        Args:
            response: Response object
            max_time: Maximum acceptable response time in seconds
            
        Returns:
            Dict: Validation result with 'valid' and 'message' keys
        """
        actual_time = response.elapsed_time
        is_valid = actual_time <= max_time
        
        result = {
            'valid': is_valid,
            'actual': actual_time,
            'expected': f"<= {max_time}"
        }
        
        if is_valid:
            result['message'] = f"Response time {actual_time:.3f}s is within limit of {max_time:.3f}s"
            self.logger.info(result['message'])
        else:
            result['message'] = f"Response time {actual_time:.3f}s exceeds limit of {max_time:.3f}s"
            self.logger.warning(result['message'])
        
        return result
