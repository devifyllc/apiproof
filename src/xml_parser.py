"""
XML Parser for the SOAP Contract Validation System.

This module provides XML parsing functionality using lxml, converting
parsed XML into XMLDocument and XMLElement data models while preserving
namespace declarations and prefixes.
"""

from pathlib import Path
from typing import Dict, Optional
from lxml import etree

from src.models import XMLDocument, XMLElement
from src.exceptions import XMLParseError


class XMLParser:
    """
    Parser for XML files and strings.
    
    This class uses lxml to parse XML content and converts it into
    XMLDocument objects with proper namespace handling.
    """
    
    def parse_file(self, file_path: Path) -> XMLDocument:
        """
        Parse an XML file into a document object.
        
        Args:
            file_path: Path to the XML file
            
        Returns:
            XMLDocument object representing the parsed XML
            
        Raises:
            XMLParseError: If the file is not valid XML
            FileNotFoundError: If the file does not exist
        """
        # Check if file exists
        if not file_path.exists():
            raise FileNotFoundError(f"XML file not found: {file_path}")
        
        try:
            # Parse the XML file with lxml
            tree = etree.parse(str(file_path))
            root_element = tree.getroot()
            
            # Extract namespace map from the root element
            namespaces = self._extract_namespaces(root_element)
            
            # Convert lxml element tree to our XMLElement model
            xml_root = self._convert_element(root_element)
            
            # Create and return XMLDocument
            return XMLDocument(
                root=xml_root,
                namespaces=namespaces,
                encoding="UTF-8"
            )
            
        except etree.XMLSyntaxError as e:
            raise XMLParseError(f"Invalid XML in file {file_path}: {str(e)}")
        except Exception as e:
            raise XMLParseError(f"Error parsing XML file {file_path}: {str(e)}")
    
    def parse_string(self, xml_string: str) -> XMLDocument:
        """
        Parse an XML string into a document object.
        
        Args:
            xml_string: XML content as a string
            
        Returns:
            XMLDocument object representing the parsed XML
            
        Raises:
            XMLParseError: If the string is not valid XML
        """
        try:
            # Parse the XML string with lxml
            root_element = etree.fromstring(xml_string.encode('utf-8'))
            
            # Extract namespace map from the root element
            namespaces = self._extract_namespaces(root_element)
            
            # Convert lxml element tree to our XMLElement model
            xml_root = self._convert_element(root_element)
            
            # Create and return XMLDocument
            return XMLDocument(
                root=xml_root,
                namespaces=namespaces,
                encoding="UTF-8"
            )
            
        except etree.XMLSyntaxError as e:
            raise XMLParseError(f"Invalid XML string: {str(e)}")
        except Exception as e:
            raise XMLParseError(f"Error parsing XML string: {str(e)}")
    
    def _extract_namespaces(self, element: etree._Element) -> Dict[str, str]:
        """
        Extract namespace declarations from an lxml element and its ancestors.
        
        This method collects all namespace prefix-to-URI mappings from the
        element's nsmap, which includes namespaces declared on the element
        and inherited from ancestors.
        
        Args:
            element: lxml Element to extract namespaces from
            
        Returns:
            Dictionary mapping namespace prefixes to URIs
        """
        namespaces = {}
        
        # Get the namespace map from the element
        nsmap = element.nsmap
        
        if nsmap:
            for prefix, uri in nsmap.items():
                # Handle default namespace (None prefix)
                if prefix is None:
                    # Store default namespace with empty string as key
                    namespaces[''] = uri
                else:
                    namespaces[prefix] = uri
        
        return namespaces
    
    def _convert_element(self, lxml_element: etree._Element) -> XMLElement:
        """
        Convert an lxml Element to an XMLElement data model.
        
        This method recursively converts an lxml element tree into our
        XMLElement data model, preserving tag names, namespaces, attributes,
        text content, and child elements.
        
        Args:
            lxml_element: lxml Element to convert
            
        Returns:
            XMLElement representation of the lxml element
        """
        # Extract tag and namespace
        tag = etree.QName(lxml_element).localname
        namespace = etree.QName(lxml_element).namespace
        
        # Extract attributes
        attributes = {}
        for attr_name, attr_value in lxml_element.attrib.items():
            # Handle namespace-qualified attributes
            attr_qname = etree.QName(attr_name)
            attributes[attr_qname.localname] = attr_value
        
        # Extract text content (strip whitespace-only text)
        text = lxml_element.text
        if text is not None:
            text = text.strip()
            if not text:
                text = None
        
        # Convert child elements recursively
        children = []
        for child in lxml_element:
            children.append(self._convert_element(child))
        
        # Create and return XMLElement
        return XMLElement(
            tag=tag,
            namespace=namespace,
            attributes=attributes,
            text=text,
            children=children
        )
