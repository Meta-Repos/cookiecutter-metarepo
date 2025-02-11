"""
Tests for plugin configuration schema validation.
"""
import pytest

from core.plugin.schema import (ConfigField, ConfigSchema, ConfigType,
                                  ValidationError, create_schema)

def test_basic_schema_validation():
    """Test basic schema validation."""
    schema = ConfigSchema([
        ConfigField(
            name="test_string",
            type=ConfigType.STRING,
            description="A test string",
            required=True
        ),
        ConfigField(
            name="test_int",
            type=ConfigType.INTEGER,
            description="A test integer",
            default=42
        )
    ])
    
    # Valid configuration
    config = {
        "test_string": "hello",
        "test_int": 123
    }
    validated = schema.validate(config)
    assert validated["test_string"] == "hello"
    assert validated["test_int"] == 123
    
    # Missing required field
    with pytest.raises(ValidationError) as exc:
        schema.validate({"test_int": 123})
    assert "Required field is missing" in str(exc.value)
    
    # Wrong type
    with pytest.raises(ValidationError) as exc:
        schema.validate({"test_string": "hello", "test_int": "not an int"})
    assert "Must be an integer" in str(exc.value)

def test_nested_schema_validation():
    """Test validation of nested schemas."""
    schema = ConfigSchema([
        ConfigField(
            name="advanced",
            type=ConfigType.DICT,
            description="Advanced settings",
            nested_schema=[
                ConfigField(
                    name="timeout",
                    type=ConfigType.FLOAT,
                    description="Timeout in seconds",
                    default=30.0
                ),
                ConfigField(
                    name="retries",
                    type=ConfigType.INTEGER,
                    description="Number of retries",
                    min_value=0,
                    max_value=10
                )
            ]
        )
    ])
    
    # Valid configuration
    config = {
        "advanced": {
            "timeout": 60.0,
            "retries": 5
        }
    }
    validated = schema.validate(config)
    assert validated["advanced"]["timeout"] == 60.0
    assert validated["advanced"]["retries"] == 5
    
    # Invalid nested value
    with pytest.raises(ValidationError) as exc:
        schema.validate({
            "advanced": {
                "timeout": 60.0,
                "retries": 20  # Exceeds max_value
            }
        })
    assert "Must be <= 10" in str(exc.value)

def test_list_schema_validation():
    """Test validation of list fields."""
    schema = ConfigSchema([
        ConfigField(
            name="features",
            type=ConfigType.LIST,
            description="Enabled features",
            nested_schema=[
                ConfigField(
                    name="feature",
                    type=ConfigType.STRING,
                    description="Feature name"
                )
            ]
        )
    ])
    
    # Valid configuration
    config = {
        "features": ["feature1", "feature2"]
    }
    validated = schema.validate(config)
    assert validated["features"] == ["feature1", "feature2"]
    
    # Invalid list item type
    with pytest.raises(ValidationError) as exc:
        schema.validate({
            "features": ["feature1", 123]
        })
    assert "Must be a string" in str(exc.value)

def test_schema_creation_from_dict():
    """Test creating a schema from a dictionary definition."""
    schema_dict = {
        "log_level": {
            "type": "string",
            "description": "Logging level",
            "choices": ["debug", "info", "warning", "error"],
            "default": "info"
        },
        "advanced": {
            "type": "dict",
            "description": "Advanced settings",
            "nested_schema": [
                {
                    "name": "timeout",
                    "type": "float",
                    "description": "Timeout in seconds",
                    "default": 30.0
                }
            ]
        }
    }
    
    schema = create_schema(schema_dict)
    
    # Valid configuration
    config = {
        "log_level": "debug",
        "advanced": {
            "timeout": 60.0
        }
    }
    validated = schema.validate(config)
    assert validated["log_level"] == "debug"
    assert validated["advanced"]["timeout"] == 60.0
    
    # Invalid choice
    with pytest.raises(ValidationError) as exc:
        schema.validate({
            "log_level": "invalid",
            "advanced": {"timeout": 60.0}
        })
    assert "Must be one of:" in str(exc.value)

def test_value_constraints():
    """Test value constraints (min, max, regex, etc.)."""
    schema = ConfigSchema([
        ConfigField(
            name="port",
            type=ConfigType.INTEGER,
            description="Port number",
            min_value=1,
            max_value=65535
        ),
        ConfigField(
            name="hostname",
            type=ConfigType.STRING,
            description="Hostname",
            regex_pattern=r"^[a-zA-Z0-9.-]+$"
        )
    ])
    
    # Valid configuration
    config = {
        "port": 8080,
        "hostname": "test-server.local"
    }
    validated = schema.validate(config)
    assert validated["port"] == 8080
    assert validated["hostname"] == "test-server.local"
    
    # Invalid port
    with pytest.raises(ValidationError) as exc:
        schema.validate({
            "port": 70000,
            "hostname": "test-server.local"
        })
    assert "Must be <= 65535" in str(exc.value)
    
    # Invalid hostname
    with pytest.raises(ValidationError) as exc:
        schema.validate({
            "port": 8080,
            "hostname": "invalid@hostname"
        })
    assert "Must match pattern" in str(exc.value)