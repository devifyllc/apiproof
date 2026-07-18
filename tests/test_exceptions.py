"""
Unit tests for the SOAP validation exception hierarchy.

Tests verify that all exceptions are properly defined, inherit correctly,
and can be raised and caught as expected.
"""

import pytest
from src.exceptions import (
    SOAPValidationError,
    XMLParseError,
    SchemaGenerationError,
    SchemaNotFoundError,
    ResponseTypeNotFoundError,
    ValidationError,
)


class TestExceptionHierarchy:
    """Test the exception inheritance hierarchy."""

    def test_soap_validation_error_is_exception(self):
        """SOAPValidationError should inherit from Exception."""
        assert issubclass(SOAPValidationError, Exception)

    def test_xml_parse_error_inherits_from_base(self):
        """XMLParseError should inherit from SOAPValidationError."""
        assert issubclass(XMLParseError, SOAPValidationError)

    def test_schema_generation_error_inherits_from_base(self):
        """SchemaGenerationError should inherit from SOAPValidationError."""
        assert issubclass(SchemaGenerationError, SOAPValidationError)

    def test_schema_not_found_error_inherits_from_base(self):
        """SchemaNotFoundError should inherit from SOAPValidationError."""
        assert issubclass(SchemaNotFoundError, SOAPValidationError)

    def test_response_type_not_found_error_inherits_from_base(self):
        """ResponseTypeNotFoundError should inherit from SOAPValidationError."""
        assert issubclass(ResponseTypeNotFoundError, SOAPValidationError)

    def test_validation_error_inherits_from_base(self):
        """ValidationError should inherit from SOAPValidationError."""
        assert issubclass(ValidationError, SOAPValidationError)


class TestExceptionRaising:
    """Test that exceptions can be raised and caught correctly."""

    def test_raise_soap_validation_error(self):
        """SOAPValidationError can be raised with a message."""
        with pytest.raises(SOAPValidationError, match="test error"):
            raise SOAPValidationError("test error")

    def test_raise_xml_parse_error(self):
        """XMLParseError can be raised with a message."""
        with pytest.raises(XMLParseError, match="parse failed"):
            raise XMLParseError("parse failed")

    def test_raise_schema_generation_error(self):
        """SchemaGenerationError can be raised with a message."""
        with pytest.raises(SchemaGenerationError, match="generation failed"):
            raise SchemaGenerationError("generation failed")

    def test_raise_schema_not_found_error(self):
        """SchemaNotFoundError can be raised with a message."""
        with pytest.raises(SchemaNotFoundError, match="schema not found"):
            raise SchemaNotFoundError("schema not found")

    def test_raise_response_type_not_found_error(self):
        """ResponseTypeNotFoundError can be raised with a message."""
        with pytest.raises(ResponseTypeNotFoundError, match="response type not found"):
            raise ResponseTypeNotFoundError("response type not found")

    def test_raise_validation_error(self):
        """ValidationError can be raised with a message."""
        with pytest.raises(ValidationError, match="validation failed"):
            raise ValidationError("validation failed")


class TestExceptionCatching:
    """Test that specific exceptions can be caught by base exception."""

    def test_catch_xml_parse_error_as_base(self):
        """XMLParseError can be caught as SOAPValidationError."""
        with pytest.raises(SOAPValidationError):
            raise XMLParseError("parse error")

    def test_catch_schema_generation_error_as_base(self):
        """SchemaGenerationError can be caught as SOAPValidationError."""
        with pytest.raises(SOAPValidationError):
            raise SchemaGenerationError("generation error")

    def test_catch_schema_not_found_error_as_base(self):
        """SchemaNotFoundError can be caught as SOAPValidationError."""
        with pytest.raises(SOAPValidationError):
            raise SchemaNotFoundError("not found error")

    def test_catch_response_type_not_found_error_as_base(self):
        """ResponseTypeNotFoundError can be caught as SOAPValidationError."""
        with pytest.raises(SOAPValidationError):
            raise ResponseTypeNotFoundError("type not found error")

    def test_catch_validation_error_as_base(self):
        """ValidationError can be caught as SOAPValidationError."""
        with pytest.raises(SOAPValidationError):
            raise ValidationError("validation error")


class TestExceptionMessages:
    """Test that exception messages are preserved correctly."""

    def test_soap_validation_error_message(self):
        """SOAPValidationError preserves the error message."""
        error = SOAPValidationError("custom message")
        assert str(error) == "custom message"

    def test_xml_parse_error_message(self):
        """XMLParseError preserves the error message."""
        error = XMLParseError("XML is malformed at line 5")
        assert str(error) == "XML is malformed at line 5"

    def test_schema_generation_error_message(self):
        """SchemaGenerationError preserves the error message."""
        error = SchemaGenerationError("Cannot infer type for element 'foo'")
        assert str(error) == "Cannot infer type for element 'foo'"

    def test_schema_not_found_error_message(self):
        """SchemaNotFoundError preserves the error message."""
        error = SchemaNotFoundError("No schema found for response type R0001")
        assert str(error) == "No schema found for response type R0001"

    def test_response_type_not_found_error_message(self):
        """ResponseTypeNotFoundError preserves the error message."""
        error = ResponseTypeNotFoundError("Cannot determine response type from XML")
        assert str(error) == "Cannot determine response type from XML"

    def test_validation_error_message(self):
        """ValidationError preserves the error message."""
        error = ValidationError("Schema validation encountered an error")
        assert str(error) == "Schema validation encountered an error"


class TestExceptionWithoutMessage:
    """Test that exceptions can be raised without messages."""

    def test_soap_validation_error_no_message(self):
        """SOAPValidationError can be raised without a message."""
        with pytest.raises(SOAPValidationError):
            raise SOAPValidationError()

    def test_xml_parse_error_no_message(self):
        """XMLParseError can be raised without a message."""
        with pytest.raises(XMLParseError):
            raise XMLParseError()

    def test_schema_generation_error_no_message(self):
        """SchemaGenerationError can be raised without a message."""
        with pytest.raises(SchemaGenerationError):
            raise SchemaGenerationError()

    def test_schema_not_found_error_no_message(self):
        """SchemaNotFoundError can be raised without a message."""
        with pytest.raises(SchemaNotFoundError):
            raise SchemaNotFoundError()

    def test_response_type_not_found_error_no_message(self):
        """ResponseTypeNotFoundError can be raised without a message."""
        with pytest.raises(ResponseTypeNotFoundError):
            raise ResponseTypeNotFoundError()

    def test_validation_error_no_message(self):
        """ValidationError can be raised without a message."""
        with pytest.raises(ValidationError):
            raise ValidationError()
