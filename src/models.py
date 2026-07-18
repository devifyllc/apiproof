"""
Data models for the SOAP Contract Validation System.

This module defines the core data structures used throughout the system,
including XML document representation, validation results, and report metadata.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional
from lxml import etree
from src.exceptions import ValidationError as ValidationException


@dataclass
class XMLElement:
    """
    Represents a single XML element with attributes and children.
    
    Attributes:
        tag: The element's tag name (without namespace prefix)
        namespace: The element's namespace URI (if any)
        attributes: Dictionary of attribute name-value pairs
        text: Text content of the element (if any)
        children: List of child XMLElement objects
    """
    tag: str
    namespace: Optional[str]
    attributes: Dict[str, str]
    text: Optional[str]
    children: List['XMLElement'] = field(default_factory=list)
    
    def get_xpath(self) -> str:
        """
        Get the XPath expression for this element.
        
        This method constructs a simple XPath by traversing up the tree.
        Note: This is a simplified implementation that doesn't handle
        sibling elements with the same tag name or complex predicates.
        
        Returns:
            XPath expression as a string (e.g., "/root/child/element")
        """
        # For now, return just the tag name
        # A full implementation would need parent references to build the complete path
        if self.namespace:
            # Return qualified name with namespace
            return f"{{{self.namespace}}}{self.tag}"
        return self.tag


@dataclass
class XMLDocument:
    """
    Represents a parsed XML document with namespace support.
    
    Attributes:
        root: The root XMLElement of the document
        namespaces: Dictionary mapping namespace prefixes to URIs
        encoding: Character encoding of the document (default: UTF-8)
    """
    root: XMLElement
    namespaces: Dict[str, str] = field(default_factory=dict)
    encoding: str = "UTF-8"
    
    def find_element(self, xpath: str) -> Optional[XMLElement]:
        """
        Find an element using XPath expression.
        
        This is a simplified XPath implementation that supports basic paths.
        For production use, consider using lxml's XPath support.
        
        Args:
            xpath: XPath expression (e.g., "/root/child/element")
            
        Returns:
            The first matching XMLElement, or None if not found
        """
        # Handle absolute paths starting with /
        if xpath.startswith('/'):
            xpath = xpath[1:]
        
        # Parse segments carefully to handle namespace URIs with slashes
        segments = []
        current_segment = ""
        in_namespace = False
        
        for char in xpath:
            if char == '{':
                in_namespace = True
                current_segment += char
            elif char == '}':
                in_namespace = False
                current_segment += char
            elif char == '/' and not in_namespace:
                if current_segment:
                    segments.append(current_segment)
                    current_segment = ""
            else:
                current_segment += char
        
        # Add the last segment
        if current_segment:
            segments.append(current_segment)
        
        if not segments:
            return None
        
        # Start from root
        current = self.root
        
        # Process first segment - check if it matches root
        first_segment = segments[0]
        if first_segment.startswith('{'):
            ns_end = first_segment.find('}')
            if ns_end > 0:
                target_ns = first_segment[1:ns_end]
                target_tag = first_segment[ns_end + 1:]
            else:
                target_tag = first_segment
                target_ns = None
        else:
            target_tag = first_segment
            target_ns = None
        
        # Check if root matches the first segment
        if current.tag != target_tag:
            return None
        if target_ns is not None and current.namespace != target_ns:
            return None
        
        # If only one segment, return root
        if len(segments) == 1:
            return current
        
        # Traverse remaining segments
        for i in range(1, len(segments)):
            segment = segments[i]
            if not segment:
                continue
                
            # Handle namespace-qualified names like {namespace}tag
            if segment.startswith('{'):
                # Extract namespace and tag
                ns_end = segment.find('}')
                if ns_end > 0:
                    target_ns = segment[1:ns_end]
                    target_tag = segment[ns_end + 1:]
                else:
                    target_tag = segment
                    target_ns = None
            else:
                target_tag = segment
                target_ns = None
            
            # Search in children for the target
            found = False
            for child in current.children:
                if child.tag == target_tag:
                    if target_ns is None or child.namespace == target_ns:
                        current = child
                        found = True
                        break
            
            if not found:
                return None
        
        return current
    
    def get_element_text(self, xpath: str) -> Optional[str]:
        """
        Get text content of an element by XPath.
        
        Args:
            xpath: XPath expression to locate the element
            
        Returns:
            Text content of the element, or None if element not found or has no text
        """
        element = self.find_element(xpath)
        if element:
            return element.text
        return None


@dataclass
class XSDSchema:
    """
    Represents an XSD schema definition.
    
    Attributes:
        schema_content: The XSD schema as XML string
        target_namespace: The target namespace URI of the schema (if any)
        response_type: Response type identifier (e.g., "R0001")
    """
    schema_content: str
    target_namespace: Optional[str]
    response_type: str
    
    def validate_document(self, document: XMLDocument) -> List[ValidationException]:
        """
        Validate an XML document against this schema.
        
        This method converts the XMLDocument to an lxml ElementTree,
        parses the XSD schema, and validates the document against it.
        Any validation errors are collected and returned as a list.
        
        Args:
            document: The XMLDocument to validate
            
        Returns:
            List of ValidationError exceptions describing any violations.
            Empty list if validation succeeds.
            
        Raises:
            ValidationError: If the schema itself is invalid or validation
                           cannot be performed (not for schema violations)
        """
        try:
            # Parse the XSD schema
            schema_doc = etree.fromstring(self.schema_content.encode('utf-8'))
            schema = etree.XMLSchema(schema_doc)
            
            # Convert XMLDocument to lxml ElementTree
            xml_element = self._convert_to_lxml(document.root, document.namespaces)
            
            # Validate the document
            is_valid = schema.validate(xml_element)
            
            if is_valid:
                return []
            
            # Collect validation errors
            errors = []
            for error in schema.error_log:
                errors.append(
                    ValidationException(
                        f"Line {error.line}: {error.message}"
                    )
                )
            
            return errors
            
        except etree.XMLSchemaParseError as e:
            raise ValidationException(f"Invalid XSD schema: {str(e)}")
        except Exception as e:
            raise ValidationException(f"Validation error: {str(e)}")
    
    def _convert_to_lxml(self, element: XMLElement, namespaces: Dict[str, str]) -> etree._Element:
        """
        Convert an XMLElement to an lxml Element.
        
        Args:
            element: The XMLElement to convert
            namespaces: Namespace prefix to URI mapping
            
        Returns:
            lxml Element representation
        """
        # Build the qualified name
        if element.namespace:
            qname = etree.QName(element.namespace, element.tag)
        else:
            qname = element.tag
        
        # Create the element
        lxml_element = etree.Element(qname, nsmap=namespaces if namespaces else None)
        
        # Add attributes
        for attr_name, attr_value in element.attributes.items():
            lxml_element.set(attr_name, attr_value)
        
        # Add text content
        if element.text is not None:
            lxml_element.text = element.text
        
        # Add children recursively
        for child in element.children:
            lxml_child = self._convert_to_lxml(child, namespaces)
            lxml_element.append(lxml_child)
        
        return lxml_element



class ViolationType(Enum):
    """
    Enumeration of contract violation types.
    
    These represent different categories of schema violations that can occur
    when validating a PROD response against a UAT-approved contract.
    """
    MISSING_REQUIRED_ELEMENT = "missing_required_element"
    UNEXPECTED_ELEMENT = "unexpected_element"
    DATA_TYPE_VIOLATION = "data_type_violation"
    INVALID_STRUCTURE = "invalid_structure"


class DifferenceType(Enum):
    """
    Enumeration of data value difference types.
    
    These represent different categories of data value differences between
    UAT and PROD responses that are not structural violations.
    """
    VALUE_CHANGED = "value_changed"
    EMPTY_TO_POPULATED = "empty_to_populated"
    POPULATED_TO_EMPTY = "populated_to_empty"


@dataclass
class ContractViolation:
    """
    Represents a single contract violation detected during validation.
    
    A contract violation occurs when a PROD response does not conform to
    the XSD schema derived from the UAT-approved response.
    
    Attributes:
        violation_type: The category of violation (e.g., missing element, type mismatch)
        element_path: XPath expression identifying the location of the violation
        description: Human-readable description of the violation
        expected: Expected value or structure according to the schema (if applicable)
        actual: Actual value or structure found in the PROD response (if applicable)
    """
    violation_type: ViolationType
    element_path: str
    description: str
    expected: Optional[str] = None
    actual: Optional[str] = None


@dataclass
class ValueDifference:
    """
    Represents a data value difference between UAT and PROD responses.
    
    A value difference is not a contract violation - it indicates that while
    the structure is valid, the actual data values differ between environments.
    
    Attributes:
        element_path: XPath expression identifying the location of the difference
        uat_value: The value in the UAT-approved response (None if empty)
        prod_value: The value in the PROD response (None if empty)
        difference_type: The category of difference (value changed, empty to populated, etc.)
    """
    element_path: str
    uat_value: Optional[str]
    prod_value: Optional[str]
    difference_type: DifferenceType


@dataclass
class ValidationResult:
    """
    Represents the result of validating a PROD response against a schema.
    
    This class encapsulates all information about a validation run, including
    whether validation succeeded, any violations found, and metadata about
    the files involved.
    
    Attributes:
        is_valid: True if the PROD response conforms to the schema, False otherwise
        violations: List of all contract violations detected
        prod_response_path: Path to the PROD response XML file
        schema_path: Path to the XSD schema file used for validation
        timestamp: When the validation was performed
    """
    is_valid: bool
    violations: List[ContractViolation]
    prod_response_path: Path
    schema_path: Path
    timestamp: datetime
    
    def has_structural_violations(self) -> bool:
        """
        Check if there are any structural violations.
        
        Structural violations include missing required elements, unexpected elements,
        and invalid structure. Data type violations are not considered structural.
        
        Returns:
            True if any structural violations exist, False otherwise
        """
        structural_types = {
            ViolationType.MISSING_REQUIRED_ELEMENT,
            ViolationType.UNEXPECTED_ELEMENT,
            ViolationType.INVALID_STRUCTURE
        }
        return any(v.violation_type in structural_types for v in self.violations)
    
    def get_violations_by_type(self, violation_type: ViolationType) -> List[ContractViolation]:
        """
        Get violations filtered by type.
        
        Args:
            violation_type: The type of violations to retrieve
            
        Returns:
            List of violations matching the specified type
        """
        return [v for v in self.violations if v.violation_type == violation_type]


@dataclass
class ReportMetadata:
    """
    Metadata included in validation reports.
    
    This class captures all contextual information about a validation run,
    including the files involved, when validation occurred, and system version.
    
    Attributes:
        uat_response_path: Path to the UAT-approved response XML file
        prod_response_path: Path to the PROD response XML file
        schema_path: Path to the XSD schema file used for validation
        validation_timestamp: When the validation was performed
        system_version: Version of the validation system
    """
    uat_response_path: Path
    prod_response_path: Path
    schema_path: Path
    validation_timestamp: datetime
    system_version: str


@dataclass
class HTMLReport:
    """
    Represents a generated HTML report.
    
    This class encapsulates an HTML validation report along with its metadata,
    and provides functionality to save the report to disk.
    
    Attributes:
        html_content: The complete HTML content as a string
        metadata: ReportMetadata containing information about the validation run
    """
    html_content: str
    metadata: ReportMetadata
    
    def save_to_file(self, output_path: Path) -> None:
        """
        Save the HTML report to a file.
        
        Creates parent directories if they don't exist and writes the HTML
        content to the specified file path.
        
        Args:
            output_path: Path where the HTML report should be saved
            
        Raises:
            IOError: If the file cannot be written
        """
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write HTML content to file
        output_path.write_text(self.html_content, encoding='utf-8')
