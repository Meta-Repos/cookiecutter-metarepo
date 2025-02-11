"""
Configuration schema validation for MetaRepos plugins.
"""
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union

class ConfigType(Enum):
    """Valid configuration value types."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"

@dataclass
class ConfigField:
    """Definition of a configuration field."""
    name: str
    type: ConfigType
    description: str
    required: bool = False
    default: Optional[Any] = None
    choices: Optional[List[Any]] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    regex_pattern: Optional[str] = None
    nested_schema: Optional[List['ConfigField']] = None

class ValidationError(Exception):
    """Raised when configuration validation fails."""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")

class ConfigSchema:
    """Configuration schema for plugin configuration."""
    
    def __init__(self, fields: List[ConfigField]):
        self.fields = {field.name: field for field in fields}
    
    def validate(self, config: Dict) -> Dict:
        """
        Validate configuration against the schema.
        Returns the validated configuration with defaults applied.
        """
        validated = {}
        
        # Check for required fields
        for name, field in self.fields.items():
            if field.required and name not in config:
                raise ValidationError(name, "Required field is missing")
        
        # Validate each field
        for name, value in config.items():
            if name not in self.fields:
                raise ValidationError(name, "Unknown configuration field")
            
            field = self.fields[name]
            validated[name] = self._validate_field(field, value)
        
        # Apply defaults for missing optional fields
        for name, field in self.fields.items():
            if name not in validated and field.default is not None:
                validated[name] = field.default
        
        return validated
    
    def _validate_field(self, field: ConfigField, value: Any) -> Any:
        """Validate a single configuration field."""
        # Check type
        if field.type == ConfigType.STRING:
            if not isinstance(value, str):
                raise ValidationError(field.name, "Must be a string")
            if field.regex_pattern and not re.match(field.regex_pattern, value):
                raise ValidationError(field.name, f"Must match pattern: {field.regex_pattern}")
        
        elif field.type == ConfigType.INTEGER:
            if not isinstance(value, int):
                raise ValidationError(field.name, "Must be an integer")
        
        elif field.type == ConfigType.FLOAT:
            if not isinstance(value, (int, float)):
                raise ValidationError(field.name, "Must be a number")
            value = float(value)
        
        elif field.type == ConfigType.BOOLEAN:
            if not isinstance(value, bool):
                raise ValidationError(field.name, "Must be a boolean")
        
        elif field.type == ConfigType.LIST:
            if not isinstance(value, list):
                raise ValidationError(field.name, "Must be a list")
            if field.nested_schema:
                value = [self._validate_field(field.nested_schema[0], item) for item in value]
        
        elif field.type == ConfigType.DICT:
            if not isinstance(value, dict):
                raise ValidationError(field.name, "Must be a dictionary")
            if field.nested_schema:
                nested_schema = ConfigSchema(field.nested_schema)
                value = nested_schema.validate(value)
        
        # Check choices
        if field.choices is not None and value not in field.choices:
            raise ValidationError(
                field.name,
                f"Must be one of: {', '.join(str(c) for c in field.choices)}"
            )
        
        # Check range
        if field.min_value is not None and value < field.min_value:
            raise ValidationError(field.name, f"Must be >= {field.min_value}")
        if field.max_value is not None and value > field.max_value:
            raise ValidationError(field.name, f"Must be <= {field.max_value}")
        
        return value

def create_schema(schema_dict: Dict) -> ConfigSchema:
    """Create a ConfigSchema from a dictionary definition."""
    fields = []
    
    for name, field_def in schema_dict.items():
        field = ConfigField(
            name=name,
            type=ConfigType(field_def["type"]),
            description=field_def.get("description", ""),
            required=field_def.get("required", False),
            default=field_def.get("default"),
            choices=field_def.get("choices"),
            min_value=field_def.get("min_value"),
            max_value=field_def.get("max_value"),
            regex_pattern=field_def.get("regex_pattern"),
            nested_schema=[
                ConfigField(**nested) for nested in field_def.get("nested_schema", [])
            ] if "nested_schema" in field_def else None
        )
        fields.append(field)
    
    return ConfigSchema(fields)