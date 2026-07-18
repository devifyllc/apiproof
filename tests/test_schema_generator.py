"""
Unit tests for the SchemaGenerator class.

This module tests the schema generation functionality, including generating
XSD schemas from UAT responses, saving schemas to files, and extracting
response type identifiers.
"""

import pytest
from pathlib import Path

from src.schema_generator import SchemaGenerator
from src.models import XMLDocument, XMLElement, XSDSchema
from src.exceptions import SchemaGenerationError, ResponseTypeNotFoundError


class TestSchemaGenerator:
    """Test suite for SchemaGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.generator = SchemaGenerator()
    
    def test_schema_generator_instantiation(self):
        """Test that SchemaGenerator can be instantiated."""
        generator = SchemaGenerator()
        assert generator is not None
        assert isinstance(generator, SchemaGenerator)
    
    def test_generate_schema_method_exists(self):
        """Test that generate_schema method exists and has correct signature."""
        assert hasattr(self.generator, 'generate_schema')
        assert callable(self.generator.generate_schema)
    
    def test_save_schema_method_exists(self):
        """Test that save_schema method exists and has correct signature."""
        assert hasattr(self.generator, 'save_schema')
        assert callable(self.generator.save_schema)
    
    def test_extract_response_type_method_exists(self):
        """Test that extract_response_type method exists and has correct signature."""
        assert hasattr(self.generator, 'extract_response_type')
        assert callable(self.generator.extract_response_type)
    
    def test_generate_schema_from_real_soap_response(self, tmp_path):
        """Test that generate_schema works with a real SOAP response structure."""
        from src.xml_parser import XMLParser
        
        # Use the actual sample file if it exists
        sample_file = Path("samples/uat-approved/R0001-approved.xml")
        if not sample_file.exists():
            pytest.skip("Sample file not found")
        
        parser = XMLParser()
        doc = parser.parse_file(sample_file)
        
        # Generate schema
        schema = self.generator.generate_schema(doc)
        
        assert schema is not None
        assert isinstance(schema, XSDSchema)
        assert schema.response_type == "R0001"
        assert schema.schema_content is not None
        assert len(schema.schema_content) > 0
        assert "xs:schema" in schema.schema_content
    
    def test_save_schema_creates_file(self, tmp_path):
        """Test that save_schema creates a file with schema content."""
        # Create a minimal XSDSchema for testing
        schema = XSDSchema(
            schema_content='<?xml version="1.0"?><xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"></xs:schema>',
            target_namespace=None,
            response_type="R0001"
        )
        output_path = tmp_path / "test_output.xsd"
        
        # Save schema
        self.generator.save_schema(schema, output_path)
        
        # Verify file was created
        assert output_path.exists()
        assert output_path.is_file()
        
        # Verify content
        content = output_path.read_text()
        assert "xs:schema" in content
    
    
    def test_extract_response_type_from_valid_soap_response(self):
        """Test extracting response type from a valid SOAP response structure."""
        # Build the SOAP structure: Envelope → Body → ServiceResponseType → ServiceResponse → R0001
        r0001_element = XMLElement(
            tag="R0001",
            namespace=None,
            attributes={},
            text=None,
            children=[]
        )
        
        service_response = XMLElement(
            tag="ServiceResponse",
            namespace=None,
            attributes={},
            text=None,
            children=[r0001_element]
        )
        
        service_response_type = XMLElement(
            tag="ServiceResponseType",
            namespace="http://wmworld/services",
            attributes={},
            text=None,
            children=[service_response]
        )
        
        body = XMLElement(
            tag="Body",
            namespace="http://schemas.xmlsoap.org/soap/envelope/",
            attributes={},
            text=None,
            children=[service_response_type]
        )
        
        envelope = XMLElement(
            tag="Envelope",
            namespace="http://schemas.xmlsoap.org/soap/envelope/",
            attributes={},
            text=None,
            children=[body]
        )
        
        doc = XMLDocument(root=envelope, namespaces={})
        
        # Extract response type
        response_type = self.generator.extract_response_type(doc)
        
        assert response_type == "R0001"
    
    def test_extract_response_type_r0002(self):
        """Test extracting different response type (R0002)."""
        # Build the SOAP structure with R0002
        r0002_element = XMLElement(
            tag="R0002",
            namespace=None,
            attributes={},
            text=None,
            children=[]
        )
        
        service_response = XMLElement(
            tag="ServiceResponse",
            namespace=None,
            attributes={},
            text=None,
            children=[r0002_element]
        )
        
        service_response_type = XMLElement(
            tag="ServiceResponseType",
            namespace="http://wmworld/services",
            attributes={},
            text=None,
            children=[service_response]
        )
        
        body = XMLElement(
            tag="Body",
            namespace="http://schemas.xmlsoap.org/soap/envelope/",
            attributes={},
            text=None,
            children=[service_response_type]
        )
        
        envelope = XMLElement(
            tag="Envelope",
            namespace="http://schemas.xmlsoap.org/soap/envelope/",
            attributes={},
            text=None,
            children=[body]
        )
        
        doc = XMLDocument(root=envelope, namespaces={})
        
        # Extract response type
        response_type = self.generator.extract_response_type(doc)
        
        assert response_type == "R0002"
    
    def test_extract_response_type_missing_body(self):
        """Test that ResponseTypeNotFoundError is raised when SOAP Body is missing."""
        # Create envelope without Body
        envelope = XMLElement(
            tag="Envelope",
            namespace="http://schemas.xmlsoap.org/soap/envelope/",
            attributes={},
            text=None,
            children=[]
        )
        
        doc = XMLDocument(root=envelope, namespaces={})
        
        with pytest.raises(ResponseTypeNotFoundError, match="SOAP Body element not found"):
            self.generator.extract_response_type(doc)
    
    def test_extract_response_type_missing_response_type_element(self):
        """Test that ResponseTypeNotFoundError is raised when *ResponseType element is missing."""
        # Create Body without *ResponseType element
        body = XMLElement(
            tag="Body",
            namespace="http://schemas.xmlsoap.org/soap/envelope/",
            attributes={},
            text=None,
            children=[]
        )
        
        envelope = XMLElement(
            tag="Envelope",
            namespace="http://schemas.xmlsoap.org/soap/envelope/",
            attributes={},
            text=None,
            children=[body]
        )
        
        doc = XMLDocument(root=envelope, namespaces={})
        
        with pytest.raises(ResponseTypeNotFoundError, match="No \\*ResponseType element found"):
            self.generator.extract_response_type(doc)
    
    def test_extract_response_type_missing_service_response(self):
        """Test that ResponseTypeNotFoundError is raised when *Response element is missing."""
        # Create ServiceResponseType without ServiceResponse
        service_response_type = XMLElement(
            tag="ServiceResponseType",
            namespace="http://wmworld/services",
            attributes={},
            text=None,
            children=[]
        )
        
        body = XMLElement(
            tag="Body",
            namespace="http://schemas.xmlsoap.org/soap/envelope/",
            attributes={},
            text=None,
            children=[service_response_type]
        )
        
        envelope = XMLElement(
            tag="Envelope",
            namespace="http://schemas.xmlsoap.org/soap/envelope/",
            attributes={},
            text=None,
            children=[body]
        )
        
        doc = XMLDocument(root=envelope, namespaces={})
        
        with pytest.raises(ResponseTypeNotFoundError, match="No \\*Response element found"):
            self.generator.extract_response_type(doc)
    
    def test_extract_response_type_missing_identifier_element(self):
        """Test that ResponseTypeNotFoundError is raised when response type identifier element (R####) is missing."""
        # Create ServiceResponse without R#### element
        service_response = XMLElement(
            tag="ServiceResponse",
            namespace=None,
            attributes={},
            text=None,
            children=[]
        )
        
        service_response_type = XMLElement(
            tag="ServiceResponseType",
            namespace="http://wmworld/services",
            attributes={},
            text=None,
            children=[service_response]
        )
        
        body = XMLElement(
            tag="Body",
            namespace="http://schemas.xmlsoap.org/soap/envelope/",
            attributes={},
            text=None,
            children=[service_response_type]
        )
        
        envelope = XMLElement(
            tag="Envelope",
            namespace="http://schemas.xmlsoap.org/soap/envelope/",
            attributes={},
            text=None,
            children=[body]
        )
        
        doc = XMLDocument(root=envelope, namespaces={})
        
        with pytest.raises(ResponseTypeNotFoundError, match="Response type element not found in ServiceResponse"):
            self.generator.extract_response_type(doc)
    
    def test_extract_response_type_with_multiple_children(self):
        """Test extracting response type when ServiceResponse has multiple children."""
        # Create StatusResponse element (another child)
        status_response = XMLElement(
            tag="StatusResponse",
            namespace=None,
            attributes={},
            text=None,
            children=[]
        )
        
        # Create R0001 element
        r0001_element = XMLElement(
            tag="R0001",
            namespace=None,
            attributes={},
            text=None,
            children=[]
        )
        
        # ServiceResponse with both R0001 and StatusResponse
        service_response = XMLElement(
            tag="ServiceResponse",
            namespace=None,
            attributes={},
            text=None,
            children=[r0001_element, status_response]
        )
        
        service_response_type = XMLElement(
            tag="ServiceResponseType",
            namespace="http://wmworld/services",
            attributes={},
            text=None,
            children=[service_response]
        )
        
        body = XMLElement(
            tag="Body",
            namespace="http://schemas.xmlsoap.org/soap/envelope/",
            attributes={},
            text=None,
            children=[service_response_type]
        )
        
        envelope = XMLElement(
            tag="Envelope",
            namespace="http://schemas.xmlsoap.org/soap/envelope/",
            attributes={},
            text=None,
            children=[body]
        )
        
        doc = XMLDocument(root=envelope, namespaces={})
        
        # Extract response type - should find R0001
        response_type = self.generator.extract_response_type(doc)
        
        assert response_type == "R0001"
    
    def test_extract_response_type_ignores_non_r_pattern_elements(self):
        """Test that elements not matching R#### pattern are ignored."""
        # Create elements that don't match the pattern
        status_response = XMLElement(
            tag="StatusResponse",
            namespace=None,
            attributes={},
            text=None,
            children=[]
        )
        
        metadata = XMLElement(
            tag="Metadata",
            namespace=None,
            attributes={},
            text=None,
            children=[]
        )
        
        # Create R0001 element
        r0001_element = XMLElement(
            tag="R0001",
            namespace=None,
            attributes={},
            text=None,
            children=[]
        )
        
        # ServiceResponse with multiple children
        service_response = XMLElement(
            tag="ServiceResponse",
            namespace=None,
            attributes={},
            text=None,
            children=[status_response, metadata, r0001_element]
        )
        
        service_response_type = XMLElement(
            tag="ServiceResponseType",
            namespace="http://wmworld/services",
            attributes={},
            text=None,
            children=[service_response]
        )
        
        body = XMLElement(
            tag="Body",
            namespace="http://schemas.xmlsoap.org/soap/envelope/",
            attributes={},
            text=None,
            children=[service_response_type]
        )
        
        envelope = XMLElement(
            tag="Envelope",
            namespace="http://schemas.xmlsoap.org/soap/envelope/",
            attributes={},
            text=None,
            children=[body]
        )
        
        doc = XMLDocument(root=envelope, namespaces={})
        
        # Extract response type - should find R0001, not StatusResponse or Metadata
        response_type = self.generator.extract_response_type(doc)
        
        assert response_type == "R0001"
