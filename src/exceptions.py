"""
Exception hierarchy for the API Contract Validation System.

This module defines all custom exceptions used throughout the system,
organized in a hierarchy with SOAPValidationError as the base exception.
"""


class SOAPValidationError(Exception):
    """Base exception for SOAP validation system."""
    pass


class XMLParseError(SOAPValidationError):
    """Raised when XML parsing fails."""
    pass


class SchemaGenerationError(SOAPValidationError):
    """Raised when schema generation fails."""
    pass


class SchemaNotFoundError(SOAPValidationError):
    """Raised when no schema exists for a response type."""
    pass


class ResponseTypeNotFoundError(SOAPValidationError):
    """Raised when response type cannot be determined."""
    pass


class ValidationError(SOAPValidationError):
    """Raised when validation encounters an error (not a violation)."""
    pass
