"""
Unit tests for the data models in src/models.py.

Tests XMLElement and XMLDocument functionality including XPath operations.
"""

import pytest
from src.models import XMLElement, XMLDocument


class TestXMLElement:
    """Tests for XMLElement data model."""
    
    def test_create_simple_element(self):
        """Test creating a simple XML element without namespace."""
        element = XMLElement(
            tag="customer",
            namespace=None,
            attributes={"id": "123"},
            text="John Doe",
            children=[]
        )
        
        assert element.tag == "customer"
        assert element.namespace is None
        assert element.attributes == {"id": "123"}
        assert element.text == "John Doe"
        assert element.children == []
    
    def test_create_element_with_namespace(self):
        """Test creating an XML element with namespace."""
        element = XMLElement(
            tag="Body",
            namespace="http://schemas.xmlsoap.org/soap/envelope/",
            attributes={},
            text=None,
            children=[]
        )
        
        assert element.tag == "Body"
        assert element.namespace == "http://schemas.xmlsoap.org/soap/envelope/"
    
    def test_create_element_with_children(self):
        """Test creating an XML element with child elements."""
        child1 = XMLElement(
            tag="firstName",
            namespace=None,
            attributes={},
            text="John",
            children=[]
        )
        child2 = XMLElement(
            tag="lastName",
            namespace=None,
            attributes={},
            text="Doe",
            children=[]
        )
        parent = XMLElement(
            tag="name",
            namespace=None,
            attributes={},
            text=None,
            children=[child1, child2]
        )
        
        assert len(parent.children) == 2
        assert parent.children[0].tag == "firstName"
        assert parent.children[1].tag == "lastName"
    
    def test_get_xpath_simple_tag(self):
        """Test get_xpath for element without namespace."""
        element = XMLElement(
            tag="customer",
            namespace=None,
            attributes={},
            text=None,
            children=[]
        )
        
        xpath = element.get_xpath()
        assert xpath == "customer"
    
    def test_get_xpath_with_namespace(self):
        """Test get_xpath for element with namespace."""
        element = XMLElement(
            tag="Body",
            namespace="http://schemas.xmlsoap.org/soap/envelope/",
            attributes={},
            text=None,
            children=[]
        )
        
        xpath = element.get_xpath()
        assert xpath == "{http://schemas.xmlsoap.org/soap/envelope/}Body"
    
    def test_element_with_empty_text(self):
        """Test element with empty string text."""
        element = XMLElement(
            tag="email",
            namespace=None,
            attributes={},
            text="",
            children=[]
        )
        
        assert element.text == ""
    
    def test_element_with_multiple_attributes(self):
        """Test element with multiple attributes."""
        element = XMLElement(
            tag="person",
            namespace=None,
            attributes={"id": "123", "type": "customer", "status": "active"},
            text=None,
            children=[]
        )
        
        assert len(element.attributes) == 3
        assert element.attributes["id"] == "123"
        assert element.attributes["type"] == "customer"
        assert element.attributes["status"] == "active"


class TestXMLDocument:
    """Tests for XMLDocument data model."""
    
    def test_create_simple_document(self):
        """Test creating a simple XML document."""
        root = XMLElement(
            tag="root",
            namespace=None,
            attributes={},
            text=None,
            children=[]
        )
        doc = XMLDocument(
            root=root,
            namespaces={},
            encoding="UTF-8"
        )
        
        assert doc.root.tag == "root"
        assert doc.encoding == "UTF-8"
        assert doc.namespaces == {}
    
    def test_create_document_with_namespaces(self):
        """Test creating a document with namespace declarations."""
        root = XMLElement(
            tag="Envelope",
            namespace="http://schemas.xmlsoap.org/soap/envelope/",
            attributes={},
            text=None,
            children=[]
        )
        doc = XMLDocument(
            root=root,
            namespaces={
                "SOAP-ENV": "http://schemas.xmlsoap.org/soap/envelope/",
                "xsd": "http://www.w3.org/2001/XMLSchema"
            },
            encoding="UTF-8"
        )
        
        assert len(doc.namespaces) == 2
        assert doc.namespaces["SOAP-ENV"] == "http://schemas.xmlsoap.org/soap/envelope/"
        assert doc.namespaces["xsd"] == "http://www.w3.org/2001/XMLSchema"
    
    def test_find_element_root(self):
        """Test finding the root element."""
        root = XMLElement(
            tag="root",
            namespace=None,
            attributes={},
            text=None,
            children=[]
        )
        doc = XMLDocument(root=root)
        
        found = doc.find_element("root")
        assert found is not None
        assert found.tag == "root"
    
    def test_find_element_child(self):
        """Test finding a child element."""
        child = XMLElement(
            tag="customer",
            namespace=None,
            attributes={},
            text="John Doe",
            children=[]
        )
        root = XMLElement(
            tag="root",
            namespace=None,
            attributes={},
            text=None,
            children=[child]
        )
        doc = XMLDocument(root=root)
        
        found = doc.find_element("root/customer")
        assert found is not None
        assert found.tag == "customer"
        assert found.text == "John Doe"
    
    def test_find_element_nested(self):
        """Test finding a deeply nested element."""
        grandchild = XMLElement(
            tag="email",
            namespace=None,
            attributes={},
            text="john@example.com",
            children=[]
        )
        child = XMLElement(
            tag="contact",
            namespace=None,
            attributes={},
            text=None,
            children=[grandchild]
        )
        root = XMLElement(
            tag="root",
            namespace=None,
            attributes={},
            text=None,
            children=[child]
        )
        doc = XMLDocument(root=root)
        
        found = doc.find_element("root/contact/email")
        assert found is not None
        assert found.tag == "email"
        assert found.text == "john@example.com"
    
    def test_find_element_not_found(self):
        """Test finding a non-existent element."""
        root = XMLElement(
            tag="root",
            namespace=None,
            attributes={},
            text=None,
            children=[]
        )
        doc = XMLDocument(root=root)
        
        found = doc.find_element("root/nonexistent")
        assert found is None
    
    def test_find_element_with_namespace(self):
        """Test finding an element with namespace qualification."""
        child = XMLElement(
            tag="Body",
            namespace="http://schemas.xmlsoap.org/soap/envelope/",
            attributes={},
            text=None,
            children=[]
        )
        root = XMLElement(
            tag="Envelope",
            namespace="http://schemas.xmlsoap.org/soap/envelope/",
            attributes={},
            text=None,
            children=[child]
        )
        doc = XMLDocument(
            root=root,
            namespaces={"SOAP-ENV": "http://schemas.xmlsoap.org/soap/envelope/"}
        )
        
        # When searching with namespace qualification, both elements need namespace in path
        found = doc.find_element("{http://schemas.xmlsoap.org/soap/envelope/}Envelope/{http://schemas.xmlsoap.org/soap/envelope/}Body")
        assert found is not None
        assert found.tag == "Body"
        assert found.namespace == "http://schemas.xmlsoap.org/soap/envelope/"
    
    def test_get_element_text_found(self):
        """Test getting text content of an element."""
        child = XMLElement(
            tag="name",
            namespace=None,
            attributes={},
            text="John Doe",
            children=[]
        )
        root = XMLElement(
            tag="root",
            namespace=None,
            attributes={},
            text=None,
            children=[child]
        )
        doc = XMLDocument(root=root)
        
        text = doc.get_element_text("root/name")
        assert text == "John Doe"
    
    def test_get_element_text_not_found(self):
        """Test getting text from non-existent element."""
        root = XMLElement(
            tag="root",
            namespace=None,
            attributes={},
            text=None,
            children=[]
        )
        doc = XMLDocument(root=root)
        
        text = doc.get_element_text("root/nonexistent")
        assert text is None
    
    def test_get_element_text_no_text(self):
        """Test getting text from element with no text content."""
        child = XMLElement(
            tag="empty",
            namespace=None,
            attributes={},
            text=None,
            children=[]
        )
        root = XMLElement(
            tag="root",
            namespace=None,
            attributes={},
            text=None,
            children=[child]
        )
        doc = XMLDocument(root=root)
        
        text = doc.get_element_text("root/empty")
        assert text is None
    
    def test_get_element_text_empty_string(self):
        """Test getting empty string text from element."""
        child = XMLElement(
            tag="field",
            namespace=None,
            attributes={},
            text="",
            children=[]
        )
        root = XMLElement(
            tag="root",
            namespace=None,
            attributes={},
            text=None,
            children=[child]
        )
        doc = XMLDocument(root=root)
        
        text = doc.get_element_text("root/field")
        assert text == ""
    
    def test_find_element_absolute_path(self):
        """Test finding element with absolute path (leading slash)."""
        child = XMLElement(
            tag="customer",
            namespace=None,
            attributes={},
            text="John",
            children=[]
        )
        root = XMLElement(
            tag="root",
            namespace=None,
            attributes={},
            text=None,
            children=[child]
        )
        doc = XMLDocument(root=root)
        
        found = doc.find_element("/root/customer")
        assert found is not None
        assert found.tag == "customer"



class TestXSDSchema:
    """Tests for XSDSchema data model."""
    
    def test_create_xsd_schema(self):
        """Test creating an XSDSchema instance."""
        from src.models import XSDSchema
        
        schema_content = """<?xml version="1.0" encoding="UTF-8"?>
        <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
            <xs:element name="root" type="xs:string"/>
        </xs:schema>"""
        
        schema = XSDSchema(
            schema_content=schema_content,
            target_namespace="http://example.com/schema",
            response_type="R0001"
        )
        
        assert schema.schema_content == schema_content
        assert schema.target_namespace == "http://example.com/schema"
        assert schema.response_type == "R0001"
    
    def test_validate_document_success(self):
        """Test validating a document that conforms to the schema."""
        from src.models import XSDSchema, XMLElement, XMLDocument
        
        # Create a simple schema that expects a root element with a string
        schema_content = """<?xml version="1.0" encoding="UTF-8"?>
        <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
            <xs:element name="root" type="xs:string"/>
        </xs:schema>"""
        
        schema = XSDSchema(
            schema_content=schema_content,
            target_namespace=None,
            response_type="R0001"
        )
        
        # Create a document that conforms to the schema
        root = XMLElement(
            tag="root",
            namespace=None,
            attributes={},
            text="Hello World",
            children=[]
        )
        doc = XMLDocument(root=root)
        
        # Validate - should return empty list (no errors)
        errors = schema.validate_document(doc)
        assert errors == []
    
    def test_validate_document_with_complex_structure(self):
        """Test validating a document with nested elements."""
        from src.models import XSDSchema, XMLElement, XMLDocument
        
        # Create a schema with nested elements
        schema_content = """<?xml version="1.0" encoding="UTF-8"?>
        <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
            <xs:element name="person">
                <xs:complexType>
                    <xs:sequence>
                        <xs:element name="name" type="xs:string"/>
                        <xs:element name="age" type="xs:integer"/>
                    </xs:sequence>
                </xs:complexType>
            </xs:element>
        </xs:schema>"""
        
        schema = XSDSchema(
            schema_content=schema_content,
            target_namespace=None,
            response_type="R0001"
        )
        
        # Create a conforming document
        name_elem = XMLElement(tag="name", namespace=None, attributes={}, text="John", children=[])
        age_elem = XMLElement(tag="age", namespace=None, attributes={}, text="30", children=[])
        root = XMLElement(
            tag="person",
            namespace=None,
            attributes={},
            text=None,
            children=[name_elem, age_elem]
        )
        doc = XMLDocument(root=root)
        
        # Validate - should succeed
        errors = schema.validate_document(doc)
        assert errors == []
    
    def test_validate_document_type_violation(self):
        """Test validating a document with data type violation."""
        from src.models import XSDSchema, XMLElement, XMLDocument
        
        # Create a schema expecting an integer
        schema_content = """<?xml version="1.0" encoding="UTF-8"?>
        <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
            <xs:element name="age" type="xs:integer"/>
        </xs:schema>"""
        
        schema = XSDSchema(
            schema_content=schema_content,
            target_namespace=None,
            response_type="R0001"
        )
        
        # Create a document with a string instead of integer
        root = XMLElement(
            tag="age",
            namespace=None,
            attributes={},
            text="not a number",
            children=[]
        )
        doc = XMLDocument(root=root)
        
        # Validate - should return errors
        errors = schema.validate_document(doc)
        assert len(errors) > 0
        assert any("not a number" in str(e) or "integer" in str(e).lower() for e in errors)
    
    def test_validate_document_missing_required_element(self):
        """Test validating a document with missing required element."""
        from src.models import XSDSchema, XMLElement, XMLDocument
        
        # Create a schema requiring two elements
        schema_content = """<?xml version="1.0" encoding="UTF-8"?>
        <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
            <xs:element name="person">
                <xs:complexType>
                    <xs:sequence>
                        <xs:element name="name" type="xs:string"/>
                        <xs:element name="age" type="xs:integer"/>
                    </xs:sequence>
                </xs:complexType>
            </xs:element>
        </xs:schema>"""
        
        schema = XSDSchema(
            schema_content=schema_content,
            target_namespace=None,
            response_type="R0001"
        )
        
        # Create a document missing the 'age' element
        name_elem = XMLElement(tag="name", namespace=None, attributes={}, text="John", children=[])
        root = XMLElement(
            tag="person",
            namespace=None,
            attributes={},
            text=None,
            children=[name_elem]
        )
        doc = XMLDocument(root=root)
        
        # Validate - should return errors about missing element
        errors = schema.validate_document(doc)
        assert len(errors) > 0
    
    def test_validate_document_with_namespace(self):
        """Test validating a document with namespace."""
        from src.models import XSDSchema, XMLElement, XMLDocument
        
        # Create a schema with target namespace
        schema_content = """<?xml version="1.0" encoding="UTF-8"?>
        <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
                   targetNamespace="http://example.com/ns"
                   xmlns:tns="http://example.com/ns"
                   elementFormDefault="qualified">
            <xs:element name="root" type="xs:string"/>
        </xs:schema>"""
        
        schema = XSDSchema(
            schema_content=schema_content,
            target_namespace="http://example.com/ns",
            response_type="R0001"
        )
        
        # Create a document with matching namespace
        root = XMLElement(
            tag="root",
            namespace="http://example.com/ns",
            attributes={},
            text="Hello",
            children=[]
        )
        doc = XMLDocument(
            root=root,
            namespaces={"tns": "http://example.com/ns"}
        )
        
        # Validate - should succeed
        errors = schema.validate_document(doc)
        assert errors == []
    
    def test_validate_document_invalid_schema(self):
        """Test that invalid schema raises ValidationError."""
        from src.models import XSDSchema, XMLElement, XMLDocument
        from src.exceptions import ValidationError
        
        # Create an invalid schema (malformed XML)
        schema_content = """<?xml version="1.0" encoding="UTF-8"?>
        <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
            <xs:element name="root" type="xs:string"
        </xs:schema>"""  # Missing closing >
        
        schema = XSDSchema(
            schema_content=schema_content,
            target_namespace=None,
            response_type="R0001"
        )
        
        root = XMLElement(tag="root", namespace=None, attributes={}, text="test", children=[])
        doc = XMLDocument(root=root)
        
        # Should raise ValidationError for invalid schema
        with pytest.raises(ValidationError):
            schema.validate_document(doc)
    
    def test_validate_document_with_attributes(self):
        """Test validating a document with attributes."""
        from src.models import XSDSchema, XMLElement, XMLDocument
        
        # Create a schema with attributes
        schema_content = """<?xml version="1.0" encoding="UTF-8"?>
        <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
            <xs:element name="person">
                <xs:complexType>
                    <xs:simpleContent>
                        <xs:extension base="xs:string">
                            <xs:attribute name="id" type="xs:string" use="required"/>
                        </xs:extension>
                    </xs:simpleContent>
                </xs:complexType>
            </xs:element>
        </xs:schema>"""
        
        schema = XSDSchema(
            schema_content=schema_content,
            target_namespace=None,
            response_type="R0001"
        )
        
        # Create a document with the required attribute
        root = XMLElement(
            tag="person",
            namespace=None,
            attributes={"id": "123"},
            text="John Doe",
            children=[]
        )
        doc = XMLDocument(root=root)
        
        # Validate - should succeed
        errors = schema.validate_document(doc)
        assert errors == []



class TestViolationType:
    """Tests for ViolationType enum."""
    
    def test_violation_type_values(self):
        """Test that all violation types have correct string values."""
        from src.models import ViolationType
        
        assert ViolationType.MISSING_REQUIRED_ELEMENT.value == "missing_required_element"
        assert ViolationType.UNEXPECTED_ELEMENT.value == "unexpected_element"
        assert ViolationType.DATA_TYPE_VIOLATION.value == "data_type_violation"
        assert ViolationType.INVALID_STRUCTURE.value == "invalid_structure"
    
    def test_violation_type_enum_members(self):
        """Test that all expected violation types exist."""
        from src.models import ViolationType
        
        expected_members = {
            "MISSING_REQUIRED_ELEMENT",
            "UNEXPECTED_ELEMENT",
            "DATA_TYPE_VIOLATION",
            "INVALID_STRUCTURE"
        }
        actual_members = {member.name for member in ViolationType}
        assert actual_members == expected_members


class TestContractViolation:
    """Tests for ContractViolation dataclass."""
    
    def test_create_violation_with_all_fields(self):
        """Test creating a contract violation with all fields."""
        from src.models import ContractViolation, ViolationType
        
        violation = ContractViolation(
            violation_type=ViolationType.MISSING_REQUIRED_ELEMENT,
            element_path="/root/customer/email",
            description="Required element 'email' is missing",
            expected="<email> element",
            actual="None"
        )
        
        assert violation.violation_type == ViolationType.MISSING_REQUIRED_ELEMENT
        assert violation.element_path == "/root/customer/email"
        assert violation.description == "Required element 'email' is missing"
        assert violation.expected == "<email> element"
        assert violation.actual == "None"
    
    def test_create_violation_with_optional_fields_none(self):
        """Test creating a contract violation with optional fields as None."""
        from src.models import ContractViolation, ViolationType
        
        violation = ContractViolation(
            violation_type=ViolationType.INVALID_STRUCTURE,
            element_path="/root/customer",
            description="Invalid structure detected"
        )
        
        assert violation.violation_type == ViolationType.INVALID_STRUCTURE
        assert violation.element_path == "/root/customer"
        assert violation.description == "Invalid structure detected"
        assert violation.expected is None
        assert violation.actual is None
    
    def test_create_data_type_violation(self):
        """Test creating a data type violation."""
        from src.models import ContractViolation, ViolationType
        
        violation = ContractViolation(
            violation_type=ViolationType.DATA_TYPE_VIOLATION,
            element_path="/root/customer/age",
            description="Expected integer, got string",
            expected="xs:integer",
            actual="'not a number'"
        )
        
        assert violation.violation_type == ViolationType.DATA_TYPE_VIOLATION
        assert "integer" in violation.description
        assert violation.expected == "xs:integer"
        assert violation.actual == "'not a number'"
    
    def test_create_unexpected_element_violation(self):
        """Test creating an unexpected element violation."""
        from src.models import ContractViolation, ViolationType
        
        violation = ContractViolation(
            violation_type=ViolationType.UNEXPECTED_ELEMENT,
            element_path="/root/customer/extraField",
            description="Unexpected element 'extraField' found",
            expected="Not present",
            actual="<extraField>value</extraField>"
        )
        
        assert violation.violation_type == ViolationType.UNEXPECTED_ELEMENT
        assert "extraField" in violation.element_path


class TestValidationResult:
    """Tests for ValidationResult dataclass."""
    
    def test_create_valid_result(self):
        """Test creating a validation result with no violations."""
        from src.models import ValidationResult
        from pathlib import Path
        from datetime import datetime
        
        result = ValidationResult(
            is_valid=True,
            violations=[],
            prod_response_path=Path("samples/prod-actual/R0001-actual.xml"),
            schema_path=Path("contracts/soap/R0001-schema.xsd"),
            timestamp=datetime(2024, 1, 15, 10, 30, 0)
        )
        
        assert result.is_valid is True
        assert result.violations == []
        assert result.prod_response_path == Path("samples/prod-actual/R0001-actual.xml")
        assert result.schema_path == Path("contracts/soap/R0001-schema.xsd")
        assert result.timestamp == datetime(2024, 1, 15, 10, 30, 0)
    
    def test_create_invalid_result_with_violations(self):
        """Test creating a validation result with violations."""
        from src.models import ValidationResult, ContractViolation, ViolationType
        from pathlib import Path
        from datetime import datetime
        
        violations = [
            ContractViolation(
                violation_type=ViolationType.MISSING_REQUIRED_ELEMENT,
                element_path="/root/customer/email",
                description="Missing required element"
            ),
            ContractViolation(
                violation_type=ViolationType.DATA_TYPE_VIOLATION,
                element_path="/root/customer/age",
                description="Type mismatch"
            )
        ]
        
        result = ValidationResult(
            is_valid=False,
            violations=violations,
            prod_response_path=Path("samples/prod-actual/R0001-actual.xml"),
            schema_path=Path("contracts/soap/R0001-schema.xsd"),
            timestamp=datetime.now()
        )
        
        assert result.is_valid is False
        assert len(result.violations) == 2
        assert result.violations[0].violation_type == ViolationType.MISSING_REQUIRED_ELEMENT
        assert result.violations[1].violation_type == ViolationType.DATA_TYPE_VIOLATION
    
    def test_has_structural_violations_true(self):
        """Test has_structural_violations returns True when structural violations exist."""
        from src.models import ValidationResult, ContractViolation, ViolationType
        from pathlib import Path
        from datetime import datetime
        
        violations = [
            ContractViolation(
                violation_type=ViolationType.MISSING_REQUIRED_ELEMENT,
                element_path="/root/customer/email",
                description="Missing required element"
            ),
            ContractViolation(
                violation_type=ViolationType.DATA_TYPE_VIOLATION,
                element_path="/root/customer/age",
                description="Type mismatch"
            )
        ]
        
        result = ValidationResult(
            is_valid=False,
            violations=violations,
            prod_response_path=Path("samples/prod-actual/R0001-actual.xml"),
            schema_path=Path("contracts/soap/R0001-schema.xsd"),
            timestamp=datetime.now()
        )
        
        # Should return True because MISSING_REQUIRED_ELEMENT is structural
        assert result.has_structural_violations() is True
    
    def test_has_structural_violations_false(self):
        """Test has_structural_violations returns False when only data type violations exist."""
        from src.models import ValidationResult, ContractViolation, ViolationType
        from pathlib import Path
        from datetime import datetime
        
        violations = [
            ContractViolation(
                violation_type=ViolationType.DATA_TYPE_VIOLATION,
                element_path="/root/customer/age",
                description="Type mismatch"
            )
        ]
        
        result = ValidationResult(
            is_valid=False,
            violations=violations,
            prod_response_path=Path("samples/prod-actual/R0001-actual.xml"),
            schema_path=Path("contracts/soap/R0001-schema.xsd"),
            timestamp=datetime.now()
        )
        
        # Should return False because DATA_TYPE_VIOLATION is not structural
        assert result.has_structural_violations() is False
    
    def test_has_structural_violations_empty(self):
        """Test has_structural_violations returns False when no violations exist."""
        from src.models import ValidationResult
        from pathlib import Path
        from datetime import datetime
        
        result = ValidationResult(
            is_valid=True,
            violations=[],
            prod_response_path=Path("samples/prod-actual/R0001-actual.xml"),
            schema_path=Path("contracts/soap/R0001-schema.xsd"),
            timestamp=datetime.now()
        )
        
        assert result.has_structural_violations() is False
    
    def test_get_violations_by_type_single_type(self):
        """Test get_violations_by_type returns violations of specified type."""
        from src.models import ValidationResult, ContractViolation, ViolationType
        from pathlib import Path
        from datetime import datetime
        
        violations = [
            ContractViolation(
                violation_type=ViolationType.MISSING_REQUIRED_ELEMENT,
                element_path="/root/customer/email",
                description="Missing email"
            ),
            ContractViolation(
                violation_type=ViolationType.DATA_TYPE_VIOLATION,
                element_path="/root/customer/age",
                description="Type mismatch"
            ),
            ContractViolation(
                violation_type=ViolationType.MISSING_REQUIRED_ELEMENT,
                element_path="/root/customer/phone",
                description="Missing phone"
            )
        ]
        
        result = ValidationResult(
            is_valid=False,
            violations=violations,
            prod_response_path=Path("samples/prod-actual/R0001-actual.xml"),
            schema_path=Path("contracts/soap/R0001-schema.xsd"),
            timestamp=datetime.now()
        )
        
        missing_violations = result.get_violations_by_type(ViolationType.MISSING_REQUIRED_ELEMENT)
        assert len(missing_violations) == 2
        assert all(v.violation_type == ViolationType.MISSING_REQUIRED_ELEMENT for v in missing_violations)
        
        type_violations = result.get_violations_by_type(ViolationType.DATA_TYPE_VIOLATION)
        assert len(type_violations) == 1
        assert type_violations[0].element_path == "/root/customer/age"
    
    def test_get_violations_by_type_no_matches(self):
        """Test get_violations_by_type returns empty list when no matches."""
        from src.models import ValidationResult, ContractViolation, ViolationType
        from pathlib import Path
        from datetime import datetime
        
        violations = [
            ContractViolation(
                violation_type=ViolationType.DATA_TYPE_VIOLATION,
                element_path="/root/customer/age",
                description="Type mismatch"
            )
        ]
        
        result = ValidationResult(
            is_valid=False,
            violations=violations,
            prod_response_path=Path("samples/prod-actual/R0001-actual.xml"),
            schema_path=Path("contracts/soap/R0001-schema.xsd"),
            timestamp=datetime.now()
        )
        
        unexpected_violations = result.get_violations_by_type(ViolationType.UNEXPECTED_ELEMENT)
        assert unexpected_violations == []
    
    def test_get_violations_by_type_all_types(self):
        """Test get_violations_by_type works for all violation types."""
        from src.models import ValidationResult, ContractViolation, ViolationType
        from pathlib import Path
        from datetime import datetime
        
        violations = [
            ContractViolation(
                violation_type=ViolationType.MISSING_REQUIRED_ELEMENT,
                element_path="/root/email",
                description="Missing"
            ),
            ContractViolation(
                violation_type=ViolationType.UNEXPECTED_ELEMENT,
                element_path="/root/extra",
                description="Unexpected"
            ),
            ContractViolation(
                violation_type=ViolationType.DATA_TYPE_VIOLATION,
                element_path="/root/age",
                description="Type error"
            ),
            ContractViolation(
                violation_type=ViolationType.INVALID_STRUCTURE,
                element_path="/root",
                description="Structure error"
            )
        ]
        
        result = ValidationResult(
            is_valid=False,
            violations=violations,
            prod_response_path=Path("samples/prod-actual/R0001-actual.xml"),
            schema_path=Path("contracts/soap/R0001-schema.xsd"),
            timestamp=datetime.now()
        )
        
        # Test each violation type
        assert len(result.get_violations_by_type(ViolationType.MISSING_REQUIRED_ELEMENT)) == 1
        assert len(result.get_violations_by_type(ViolationType.UNEXPECTED_ELEMENT)) == 1
        assert len(result.get_violations_by_type(ViolationType.DATA_TYPE_VIOLATION)) == 1
        assert len(result.get_violations_by_type(ViolationType.INVALID_STRUCTURE)) == 1
    
    def test_structural_violation_types(self):
        """Test that structural violation detection includes correct types."""
        from src.models import ValidationResult, ContractViolation, ViolationType
        from pathlib import Path
        from datetime import datetime
        
        # Test UNEXPECTED_ELEMENT is structural
        result1 = ValidationResult(
            is_valid=False,
            violations=[
                ContractViolation(
                    violation_type=ViolationType.UNEXPECTED_ELEMENT,
                    element_path="/root/extra",
                    description="Unexpected"
                )
            ],
            prod_response_path=Path("test.xml"),
            schema_path=Path("test.xsd"),
            timestamp=datetime.now()
        )
        assert result1.has_structural_violations() is True
        
        # Test INVALID_STRUCTURE is structural
        result2 = ValidationResult(
            is_valid=False,
            violations=[
                ContractViolation(
                    violation_type=ViolationType.INVALID_STRUCTURE,
                    element_path="/root",
                    description="Invalid"
                )
            ],
            prod_response_path=Path("test.xml"),
            schema_path=Path("test.xsd"),
            timestamp=datetime.now()
        )
        assert result2.has_structural_violations() is True



class TestDifferenceType:
    """Tests for DifferenceType enum."""
    
    def test_difference_type_values(self):
        """Test that all difference types have correct string values."""
        from src.models import DifferenceType
        
        assert DifferenceType.VALUE_CHANGED.value == "value_changed"
        assert DifferenceType.EMPTY_TO_POPULATED.value == "empty_to_populated"
        assert DifferenceType.POPULATED_TO_EMPTY.value == "populated_to_empty"
    
    def test_difference_type_enum_members(self):
        """Test that all expected difference types exist."""
        from src.models import DifferenceType
        
        expected_members = {
            "VALUE_CHANGED",
            "EMPTY_TO_POPULATED",
            "POPULATED_TO_EMPTY"
        }
        actual_members = {member.name for member in DifferenceType}
        assert actual_members == expected_members


class TestValueDifference:
    """Tests for ValueDifference dataclass."""
    
    def test_create_value_changed_difference(self):
        """Test creating a value difference for changed values."""
        from src.models import ValueDifference, DifferenceType
        
        diff = ValueDifference(
            element_path="/root/customer/name",
            uat_value="John Doe",
            prod_value="Jane Smith",
            difference_type=DifferenceType.VALUE_CHANGED
        )
        
        assert diff.element_path == "/root/customer/name"
        assert diff.uat_value == "John Doe"
        assert diff.prod_value == "Jane Smith"
        assert diff.difference_type == DifferenceType.VALUE_CHANGED
    
    def test_create_empty_to_populated_difference(self):
        """Test creating a difference for empty to populated transition."""
        from src.models import ValueDifference, DifferenceType
        
        diff = ValueDifference(
            element_path="/root/customer/email",
            uat_value=None,
            prod_value="john@example.com",
            difference_type=DifferenceType.EMPTY_TO_POPULATED
        )
        
        assert diff.element_path == "/root/customer/email"
        assert diff.uat_value is None
        assert diff.prod_value == "john@example.com"
        assert diff.difference_type == DifferenceType.EMPTY_TO_POPULATED
    
    def test_create_populated_to_empty_difference(self):
        """Test creating a difference for populated to empty transition."""
        from src.models import ValueDifference, DifferenceType
        
        diff = ValueDifference(
            element_path="/root/customer/phone",
            uat_value="555-1234",
            prod_value=None,
            difference_type=DifferenceType.POPULATED_TO_EMPTY
        )
        
        assert diff.element_path == "/root/customer/phone"
        assert diff.uat_value == "555-1234"
        assert diff.prod_value is None
        assert diff.difference_type == DifferenceType.POPULATED_TO_EMPTY
    
    def test_create_difference_with_empty_strings(self):
        """Test creating a difference with empty string values."""
        from src.models import ValueDifference, DifferenceType
        
        diff = ValueDifference(
            element_path="/root/customer/middleName",
            uat_value="",
            prod_value="Michael",
            difference_type=DifferenceType.EMPTY_TO_POPULATED
        )
        
        assert diff.element_path == "/root/customer/middleName"
        assert diff.uat_value == ""
        assert diff.prod_value == "Michael"
        assert diff.difference_type == DifferenceType.EMPTY_TO_POPULATED
    
    def test_create_difference_with_xpath(self):
        """Test creating a difference with complex XPath."""
        from src.models import ValueDifference, DifferenceType
        
        diff = ValueDifference(
            element_path="/SOAP-ENV:Envelope/SOAP-ENV:Body/ns:Response/ns:Customer/ns:Address/ns:City",
            uat_value="New York",
            prod_value="Los Angeles",
            difference_type=DifferenceType.VALUE_CHANGED
        )
        
        assert "/SOAP-ENV:Envelope" in diff.element_path
        assert diff.uat_value == "New York"
        assert diff.prod_value == "Los Angeles"
    
    def test_difference_not_a_violation(self):
        """Test that ValueDifference is distinct from ContractViolation."""
        from src.models import ValueDifference, DifferenceType, ContractViolation, ViolationType
        
        # Create a value difference
        diff = ValueDifference(
            element_path="/root/customer/name",
            uat_value="John",
            prod_value="Jane",
            difference_type=DifferenceType.VALUE_CHANGED
        )
        
        # Create a contract violation
        violation = ContractViolation(
            violation_type=ViolationType.MISSING_REQUIRED_ELEMENT,
            element_path="/root/customer/email",
            description="Missing required element"
        )
        
        # They should be different types
        assert type(diff).__name__ == "ValueDifference"
        assert type(violation).__name__ == "ContractViolation"
        assert not isinstance(diff, type(violation))



class TestReportMetadata:
    """Tests for ReportMetadata dataclass."""
    
    def test_create_report_metadata(self):
        """Test creating a ReportMetadata instance with all fields."""
        from src.models import ReportMetadata
        from pathlib import Path
        from datetime import datetime
        
        metadata = ReportMetadata(
            uat_response_path=Path("samples/uat-approved/R0001-approved.xml"),
            prod_response_path=Path("samples/prod-actual/R0001-actual.xml"),
            schema_path=Path("contracts/soap/R0001-schema.xsd"),
            validation_timestamp=datetime(2024, 1, 15, 10, 30, 0),
            system_version="1.0.0"
        )
        
        assert metadata.uat_response_path == Path("samples/uat-approved/R0001-approved.xml")
        assert metadata.prod_response_path == Path("samples/prod-actual/R0001-actual.xml")
        assert metadata.schema_path == Path("contracts/soap/R0001-schema.xsd")
        assert metadata.validation_timestamp == datetime(2024, 1, 15, 10, 30, 0)
        assert metadata.system_version == "1.0.0"
    
    def test_report_metadata_with_different_paths(self):
        """Test ReportMetadata with different file paths."""
        from src.models import ReportMetadata
        from pathlib import Path
        from datetime import datetime
        
        metadata = ReportMetadata(
            uat_response_path=Path("data/uat/R0002-approved.xml"),
            prod_response_path=Path("data/prod/R0002-actual.xml"),
            schema_path=Path("schemas/R0002-schema.xsd"),
            validation_timestamp=datetime.now(),
            system_version="2.1.3"
        )
        
        assert metadata.uat_response_path.name == "R0002-approved.xml"
        assert metadata.prod_response_path.name == "R0002-actual.xml"
        assert metadata.schema_path.name == "R0002-schema.xsd"
        assert metadata.system_version == "2.1.3"
    
    def test_report_metadata_timestamp_format(self):
        """Test that ReportMetadata stores timestamp correctly."""
        from src.models import ReportMetadata
        from pathlib import Path
        from datetime import datetime
        
        timestamp = datetime(2024, 3, 15, 14, 30, 45)
        metadata = ReportMetadata(
            uat_response_path=Path("uat.xml"),
            prod_response_path=Path("prod.xml"),
            schema_path=Path("schema.xsd"),
            validation_timestamp=timestamp,
            system_version="1.0.0"
        )
        
        assert metadata.validation_timestamp.year == 2024
        assert metadata.validation_timestamp.month == 3
        assert metadata.validation_timestamp.day == 15
        assert metadata.validation_timestamp.hour == 14
        assert metadata.validation_timestamp.minute == 30
        assert metadata.validation_timestamp.second == 45


class TestHTMLReport:
    """Tests for HTMLReport dataclass."""
    
    def test_create_html_report(self):
        """Test creating an HTMLReport instance."""
        from src.models import HTMLReport, ReportMetadata
        from pathlib import Path
        from datetime import datetime
        
        metadata = ReportMetadata(
            uat_response_path=Path("samples/uat-approved/R0001-approved.xml"),
            prod_response_path=Path("samples/prod-actual/R0001-actual.xml"),
            schema_path=Path("contracts/soap/R0001-schema.xsd"),
            validation_timestamp=datetime(2024, 1, 15, 10, 30, 0),
            system_version="1.0.0"
        )
        
        html_content = "<html><body><h1>Validation Report</h1></body></html>"
        
        report = HTMLReport(
            html_content=html_content,
            metadata=metadata
        )
        
        assert report.html_content == html_content
        assert report.metadata == metadata
        assert report.metadata.system_version == "1.0.0"
    
    def test_save_to_file_creates_file(self, tmp_path):
        """Test that save_to_file creates an HTML file."""
        from src.models import HTMLReport, ReportMetadata
        from pathlib import Path
        from datetime import datetime
        
        metadata = ReportMetadata(
            uat_response_path=Path("uat.xml"),
            prod_response_path=Path("prod.xml"),
            schema_path=Path("schema.xsd"),
            validation_timestamp=datetime.now(),
            system_version="1.0.0"
        )
        
        html_content = "<html><body><h1>Test Report</h1></body></html>"
        report = HTMLReport(html_content=html_content, metadata=metadata)
        
        # Save to temporary directory
        output_path = tmp_path / "report.html"
        report.save_to_file(output_path)
        
        # Verify file was created
        assert output_path.exists()
        assert output_path.is_file()
    
    def test_save_to_file_writes_correct_content(self, tmp_path):
        """Test that save_to_file writes the correct HTML content."""
        from src.models import HTMLReport, ReportMetadata
        from pathlib import Path
        from datetime import datetime
        
        metadata = ReportMetadata(
            uat_response_path=Path("uat.xml"),
            prod_response_path=Path("prod.xml"),
            schema_path=Path("schema.xsd"),
            validation_timestamp=datetime.now(),
            system_version="1.0.0"
        )
        
        html_content = "<html><body><h1>Validation Report</h1><p>Status: PASS</p></body></html>"
        report = HTMLReport(html_content=html_content, metadata=metadata)
        
        # Save to temporary directory
        output_path = tmp_path / "validation-report.html"
        report.save_to_file(output_path)
        
        # Read back and verify content
        saved_content = output_path.read_text(encoding='utf-8')
        assert saved_content == html_content
        assert "<h1>Validation Report</h1>" in saved_content
        assert "Status: PASS" in saved_content
    
    def test_save_to_file_creates_parent_directories(self, tmp_path):
        """Test that save_to_file creates parent directories if they don't exist."""
        from src.models import HTMLReport, ReportMetadata
        from pathlib import Path
        from datetime import datetime
        
        metadata = ReportMetadata(
            uat_response_path=Path("uat.xml"),
            prod_response_path=Path("prod.xml"),
            schema_path=Path("schema.xsd"),
            validation_timestamp=datetime.now(),
            system_version="1.0.0"
        )
        
        html_content = "<html><body><h1>Report</h1></body></html>"
        report = HTMLReport(html_content=html_content, metadata=metadata)
        
        # Save to nested directory that doesn't exist
        output_path = tmp_path / "reports" / "validation" / "report.html"
        report.save_to_file(output_path)
        
        # Verify file and directories were created
        assert output_path.exists()
        assert output_path.parent.exists()
        assert output_path.parent.parent.exists()
    
    def test_save_to_file_overwrites_existing(self, tmp_path):
        """Test that save_to_file overwrites existing file."""
        from src.models import HTMLReport, ReportMetadata
        from pathlib import Path
        from datetime import datetime
        
        metadata = ReportMetadata(
            uat_response_path=Path("uat.xml"),
            prod_response_path=Path("prod.xml"),
            schema_path=Path("schema.xsd"),
            validation_timestamp=datetime.now(),
            system_version="1.0.0"
        )
        
        output_path = tmp_path / "report.html"
        
        # Create initial file
        initial_content = "<html><body><h1>Old Report</h1></body></html>"
        report1 = HTMLReport(html_content=initial_content, metadata=metadata)
        report1.save_to_file(output_path)
        
        # Overwrite with new content
        new_content = "<html><body><h1>New Report</h1></body></html>"
        report2 = HTMLReport(html_content=new_content, metadata=metadata)
        report2.save_to_file(output_path)
        
        # Verify new content replaced old content
        saved_content = output_path.read_text(encoding='utf-8')
        assert saved_content == new_content
        assert "New Report" in saved_content
        assert "Old Report" not in saved_content
    
    def test_save_to_file_with_utf8_content(self, tmp_path):
        """Test that save_to_file handles UTF-8 content correctly."""
        from src.models import HTMLReport, ReportMetadata
        from pathlib import Path
        from datetime import datetime
        
        metadata = ReportMetadata(
            uat_response_path=Path("uat.xml"),
            prod_response_path=Path("prod.xml"),
            schema_path=Path("schema.xsd"),
            validation_timestamp=datetime.now(),
            system_version="1.0.0"
        )
        
        # HTML content with special characters
        html_content = "<html><body><h1>Validation Report</h1><p>Status: ✓ PASS</p><p>Customer: José García</p></body></html>"
        report = HTMLReport(html_content=html_content, metadata=metadata)
        
        output_path = tmp_path / "report-utf8.html"
        report.save_to_file(output_path)
        
        # Read back and verify UTF-8 content
        saved_content = output_path.read_text(encoding='utf-8')
        assert saved_content == html_content
        assert "✓" in saved_content
        assert "José García" in saved_content
    
    def test_html_report_with_complex_content(self):
        """Test HTMLReport with complex HTML content."""
        from src.models import HTMLReport, ReportMetadata
        from pathlib import Path
        from datetime import datetime
        
        metadata = ReportMetadata(
            uat_response_path=Path("samples/uat-approved/R0001-approved.xml"),
            prod_response_path=Path("samples/prod-actual/R0001-actual.xml"),
            schema_path=Path("contracts/soap/R0001-schema.xsd"),
            validation_timestamp=datetime(2024, 1, 15, 10, 30, 0),
            system_version="1.0.0"
        )
        
        html_content = """<!DOCTYPE html>
<html>
<head>
    <title>SOAP Contract Validation Report</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .pass { color: green; }
        .fail { color: red; }
    </style>
</head>
<body>
    <h1>Validation Report</h1>
    <div class="pass">Status: PASS</div>
    <table>
        <tr><td>UAT Response</td><td>samples/uat-approved/R0001-approved.xml</td></tr>
        <tr><td>PROD Response</td><td>samples/prod-actual/R0001-actual.xml</td></tr>
    </table>
</body>
</html>"""
        
        report = HTMLReport(html_content=html_content, metadata=metadata)
        
        assert "<!DOCTYPE html>" in report.html_content
        assert "<style>" in report.html_content
        assert "Validation Report" in report.html_content
        assert report.metadata.uat_response_path.name == "R0001-approved.xml"
