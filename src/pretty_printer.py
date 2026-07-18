"""
Pretty printer for XML documents.

This module provides functionality to format XML documents and elements
into readable, well-formed strings with consistent indentation.
"""

from lxml import etree
from src.models import XMLDocument, XMLElement
from typing import Dict


class PrettyPrinter:
    """
    Formats XML documents and elements into pretty-printed strings.
    
    This class uses lxml to format XML with consistent indentation,
    preserving namespace declarations and handling empty elements appropriately.
    """
    
    def __init__(self, indent_spaces: int = 4):
        """
        Initialize the PrettyPrinter.
        
        Args:
            indent_spaces: Number of spaces to use for indentation (default: 4)
        """
        self.indent_spaces = indent_spaces
    
    def format_xml(self, document: XMLDocument) -> str:
        """
        Format an XML document into a pretty-printed string.
        
        This method converts the XMLDocument to an lxml ElementTree,
        applies pretty-printing with consistent indentation, and returns
        the formatted XML string with XML declaration.
        
        Args:
            document: XML document to format
            
        Returns:
            Formatted XML string with consistent indentation
        """
        # Convert XMLDocument to lxml Element
        root_element = self._convert_to_lxml(document.root, document.namespaces)
        
        # Create an ElementTree from the root
        tree = etree.ElementTree(root_element)
        
        # Apply indentation
        etree.indent(tree, space=' ' * self.indent_spaces)
        
        # Convert to string with XML declaration
        xml_bytes = etree.tostring(
            tree,
            encoding=document.encoding,
            xml_declaration=True,
            pretty_print=True
        )
        
        # Decode to string
        return xml_bytes.decode(document.encoding)
    
    def format_element(self, element: XMLElement) -> str:
        """
        Format a single XML element into a string.
        
        This method converts a single XMLElement to an lxml Element,
        applies pretty-printing, and returns the formatted XML string
        without an XML declaration.
        
        Args:
            element: XML element to format
            
        Returns:
            Formatted XML string for the element
        """
        # Convert XMLElement to lxml Element
        # Use empty namespace map for single element formatting
        lxml_element = self._convert_to_lxml(element, {})
        
        # Apply indentation
        etree.indent(lxml_element, space=' ' * self.indent_spaces)
        
        # Convert to string without XML declaration
        xml_bytes = etree.tostring(
            lxml_element,
            encoding='UTF-8',
            xml_declaration=False,
            pretty_print=True
        )
        
        # Decode to string and strip trailing whitespace
        return xml_bytes.decode('UTF-8').rstrip()
    
    def _convert_to_lxml(self, element: XMLElement, namespaces: Dict[str, str]) -> etree._Element:
        """
        Convert an XMLElement to an lxml Element.
        
        This method recursively converts XMLElement objects to lxml Elements,
        preserving namespaces, attributes, text content, and child elements.
        
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
        
        # Create the element with namespace map
        # Only include namespaces on the root element to avoid duplication
        nsmap = namespaces if namespaces else None
        lxml_element = etree.Element(qname, nsmap=nsmap)
        
        # Add attributes
        for attr_name, attr_value in element.attributes.items():
            lxml_element.set(attr_name, attr_value)
        
        # Add text content
        if element.text is not None:
            lxml_element.text = element.text
        
        # Add children recursively
        # Pass empty dict for namespaces to avoid redeclaring them on children
        for child in element.children:
            lxml_child = self._convert_to_lxml(child, {})
            lxml_element.append(lxml_child)
        
        return lxml_element
