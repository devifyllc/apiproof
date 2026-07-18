"""
Schema Generator for the SOAP Contract Validation System.

This module provides functionality to generate XSD schemas from UAT-approved
SOAP responses. The generated schemas serve as formal contract baselines for
validating PROD responses.
"""

from pathlib import Path
from typing import Optional, Dict

from src.models import XMLDocument, XSDSchema, XMLElement
from src.exceptions import SchemaGenerationError, ResponseTypeNotFoundError


class SchemaGenerator:
    """
    Generator for XSD schemas from UAT-approved SOAP responses.
    
    This class analyzes UAT-approved SOAP responses and generates corresponding
    XSD schemas that define the structure, elements, and data types of valid
    SOAP responses. The generated schemas are used to validate PROD responses
    against the UAT-approved contract baseline.
    """
    
    def generate_schema(self, uat_response: XMLDocument) -> XSDSchema:
        """
        Generate an XSD schema from a UAT-approved SOAP response.
        
        This method analyzes the structure of a UAT-approved SOAP response,
        extracts all elements, attributes, and data types, and generates a
        formal XSD schema that defines the valid structure for this response type.
        
        The generated schema is permissive:
        - All elements are optional (minOccurs="0")
        - All elements allow unbounded repetition (maxOccurs="unbounded")
        - All elements use xs:string type (simplification for MVP)
        - Namespace declarations are preserved
        
        Args:
            uat_response: Parsed UAT SOAP response document
            
        Returns:
            XSDSchema object representing the generated schema
            
        Raises:
            SchemaGenerationError: If schema generation fails
        """
        try:
            # Extract response type for schema metadata
            response_type = self.extract_response_type(uat_response)
            
            # Analyze XML structure to catalog all elements
            element_catalog = self._analyze_structure(uat_response.root)
            
            # Generate XSD schema content
            schema_content = self._build_xsd_schema(
                element_catalog, 
                uat_response.namespaces,
                uat_response.root
            )
            
            # Extract target namespace (if any)
            target_namespace = uat_response.root.namespace
            
            return XSDSchema(
                schema_content=schema_content,
                target_namespace=target_namespace,
                response_type=response_type
            )
            
        except ResponseTypeNotFoundError:
            # Re-raise ResponseTypeNotFoundError as-is
            raise
        except Exception as e:
            raise SchemaGenerationError(
                f"Failed to generate schema: {str(e)}"
            )
    
    def save_schema(self, schema: XSDSchema, output_path: Path) -> None:
        """
        Save an XSD schema to a file.
        
        This method writes an XSD schema to disk at the specified location,
        creating parent directories if necessary. The schema is saved as a
        well-formed XML document.
        
        Args:
            schema: The XSD schema to save
            output_path: Path where the schema file should be saved
            
        Raises:
            IOError: If the file cannot be written
        """
        try:
            # Ensure parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write schema content to file
            output_path.write_text(schema.schema_content, encoding='utf-8')
            
        except Exception as e:
            raise IOError(f"Failed to save schema to {output_path}: {str(e)}")
    
    def extract_response_type(self, uat_response: XMLDocument) -> str:
        """
        Extract the response type identifier (e.g., "R0001", "LOV_TITLE") from a SOAP response.
        
        This method analyzes a SOAP response to identify the response type
        identifier, which is used to name schema files and match PROD responses
        to their corresponding schemas. The response type is typically found as
        an element name within the SOAP body.
        
        The expected structure is:
        SOAP-ENV:Envelope → SOAP-ENV:Body → m:*ResponseType → *Response → ResponseTypeElement
        
        Args:
            uat_response: Parsed UAT SOAP response document
            
        Returns:
            Response type identifier string (e.g., "R0001", "LOV_TITLE")
            
        Raises:
            ResponseTypeNotFoundError: If response type cannot be determined
        """
        try:
            # Navigate to SOAP Body
            soap_body = uat_response.find_element(
                "{http://schemas.xmlsoap.org/soap/envelope/}Envelope/"
                "{http://schemas.xmlsoap.org/soap/envelope/}Body"
            )
            
            if not soap_body:
                raise ResponseTypeNotFoundError(
                    "SOAP Body element not found in response"
                )
            
            # Navigate to first child of SOAP Body (e.g., ServiceResponseType, *ResponseType)
            # This is flexible to handle any naming convention
            response_type_element = None
            for child in soap_body.children:
                if child.tag.endswith("ResponseType"):
                    response_type_element = child
                    break
            
            if not response_type_element:
                raise ResponseTypeNotFoundError(
                    "No *ResponseType element found in SOAP Body"
                )
            
            # Navigate to first child ending with "Response" (e.g., ServiceResponse, *Response)
            response_element = None
            for child in response_type_element.children:
                if child.tag.endswith("Response"):
                    response_element = child
                    break
            
            if not response_element:
                raise ResponseTypeNotFoundError(
                    f"No *Response element found in {response_type_element.tag}"
                )
            
            # Find the response type element
            # Strategy 1: Look for R#### pattern (e.g., R0001, R0002)
            for child in response_element.children:
                # Check if the tag matches the response type pattern (R followed by digits)
                if child.tag.startswith('R') and len(child.tag) > 1:
                    # Verify it's R followed by digits
                    if child.tag[1:].isdigit():
                        return child.tag
            
            # Strategy 2: If no R#### pattern found, use the first child element name
            # This handles cases like SSR, GETCONTACTQA_213, LOV_TITLE, GetListOfValues, etc.
            if response_element.children:
                # Skip StatusResponse if it's the only child or first child
                for child in response_element.children:
                    if child.tag != "StatusResponse":
                        return child.tag
                
                # If only StatusResponse exists, use it
                return response_element.children[0].tag
            
            raise ResponseTypeNotFoundError(
                f"Response type element not found in {response_element.tag} (no child elements)"
            )
            
        except ResponseTypeNotFoundError:
            # Re-raise ResponseTypeNotFoundError as-is
            raise
        except Exception as e:
            raise ResponseTypeNotFoundError(
                f"Failed to extract response type: {str(e)}"
            )
    
    def _analyze_structure(self, element: XMLElement) -> dict:
        """
        Analyze XML structure depth-first to catalog all elements.
        
        This method traverses the XML tree and extracts:
        - Element names
        - Attributes
        - Nesting relationships
        - Cardinality (repeating elements)
        
        Args:
            element: The root XMLElement to analyze
            
        Returns:
            Dictionary mapping element paths to element metadata
        """
        catalog = {}
        
        def traverse(elem: XMLElement, path: str = ""):
            # Build current element path
            if elem.namespace:
                current_path = f"{path}/{{{elem.namespace}}}{elem.tag}"
            else:
                current_path = f"{path}/{elem.tag}"
            
            # Catalog this element
            if current_path not in catalog:
                catalog[current_path] = {
                    'tag': elem.tag,
                    'namespace': elem.namespace,
                    'attributes': list(elem.attributes.keys()),
                    'has_text': elem.text is not None and elem.text.strip() != '',
                    'children': []
                }
            
            # Traverse children
            for child in elem.children:
                child_tag = child.tag
                if child_tag not in catalog[current_path]['children']:
                    catalog[current_path]['children'].append(child_tag)
                traverse(child, current_path)
        
        traverse(element)
        return catalog
    
    def _build_xsd_schema(self, element_catalog: dict, namespaces: dict, root: XMLElement) -> str:
        """
        Build XSD schema definition from analyzed structure.
        
        This method generates a permissive XSD schema that:
        - Makes all elements optional (minOccurs="0")
        - Allows unbounded repetition (maxOccurs="unbounded")
        - Uses xs:string for all element types
        - Preserves namespace declarations
        - Uses xs:any for flexible namespace handling
        
        Args:
            element_catalog: Dictionary of element metadata from structure analysis
            namespaces: Namespace prefix to URI mapping
            root: The root XMLElement
            
        Returns:
            XSD schema as XML string
        """
        from lxml import etree
        
        # Define XSD namespace
        XS_NS = "http://www.w3.org/2001/XMLSchema"
        XS = "{%s}" % XS_NS
        
        # Create schema root element
        nsmap = {
            'xs': XS_NS
        }
        
        # Add original namespaces to schema
        for prefix, uri in namespaces.items():
            if prefix and prefix != 'xs':
                nsmap[prefix] = uri
        
        schema_elem = etree.Element(
            XS + "schema",
            nsmap=nsmap,
            elementFormDefault="qualified"
        )
        
        # Set target namespace if root has one
        if root.namespace:
            schema_elem.set("targetNamespace", root.namespace)
        
        # Generate element definitions recursively with namespace awareness
        self._generate_element_definitions_permissive(schema_elem, root, element_catalog, XS)
        
        # Convert to string with pretty printing
        schema_content = etree.tostring(
            schema_elem,
            pretty_print=True,
            xml_declaration=True,
            encoding='UTF-8'
        ).decode('utf-8')
        
        return schema_content
    
    def _generate_element_definitions_permissive(self, schema_elem, element: XMLElement, 
                                                 element_catalog: dict, XS: str) -> None:
        """
        Generate XSD element definitions with permissive namespace handling.
        
        This creates a schema that allows any content in the SOAP body,
        making it very permissive for validation purposes.
        
        Args:
            schema_elem: The XSD schema element to append definitions to
            element: The XMLElement to generate definition for
            element_catalog: Dictionary of element metadata
            XS: XSD namespace prefix string
        """
        from lxml import etree
        
        # Create the root Envelope element definition
        envelope_elem = etree.Element(XS + "element", name=element.tag)
        
        # Create complex type for Envelope
        envelope_complex = etree.SubElement(envelope_elem, XS + "complexType")
        envelope_seq = etree.SubElement(envelope_complex, XS + "sequence")
        
        # Add Header and Body as flexible elements
        for child in element.children:
            if child.tag in ["Header", "Body"]:
                child_elem = etree.SubElement(envelope_seq, XS + "element", name=child.tag)
                child_elem.set("minOccurs", "0")
                child_elem.set("maxOccurs", "unbounded")
                
                # Create complex type with xs:any for flexible content
                child_complex = etree.SubElement(child_elem, XS + "complexType")
                child_seq = etree.SubElement(child_complex, XS + "sequence")
                
                # Add xs:any to allow any content
                any_elem = etree.SubElement(child_seq, XS + "any")
                any_elem.set("minOccurs", "0")
                any_elem.set("maxOccurs", "unbounded")
                any_elem.set("processContents", "lax")
                any_elem.set("namespace", "##any")
        
        schema_elem.append(envelope_elem)
