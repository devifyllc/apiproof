"""
Unit tests for the XMLParser class.

**Validates: Requirements 4.1**

This module tests XML parsing functionality including file parsing,
string parsing, namespace handling, and error conditions.
"""

import pytest
from pathlib import Path
from src.xml_parser import XMLParser
from src.exceptions import XMLParseError
from src.models import XMLDocument, XMLElement


class TestXMLParserBasicParsing:
    """Test basic XML parsing functionality."""
    
    def test_parse_simple_xml_string(self):
        """Test parsing a simple XML string without namespaces."""
        parser = XMLParser()
        xml_string = '<?xml version="1.0"?><root><child>text</child></root>'
        
        doc = parser.parse_string(xml_string)
        
        assert isinstance(doc, XMLDocument)
        assert doc.root.tag == "root"
        assert len(doc.root.children) == 1
        assert doc.root.children[0].tag == "child"
        assert doc.root.children[0].text == "text"
    
    def test_parse_xml_with_attributes(self):
        """Test parsing XML with attributes."""
        parser = XMLParser()
        xml_string = '<root id="123" name="test"><child attr="value"/></root>'
        
        doc = parser.parse_string(xml_string)
        
        assert doc.root.attributes["id"] == "123"
        assert doc.root.attributes["name"] == "test"
        assert doc.root.children[0].attributes["attr"] == "value"
    
    def test_parse_xml_with_namespaces(self):
        """Test parsing XML with namespace declarations."""
        parser = XMLParser()
        xml_string = '''<?xml version="1.0"?>
        <root xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
            <soap:body>content</soap:body>
        </root>'''
        
        doc = parser.parse_string(xml_string)
        
        assert "soap" in doc.namespaces
        assert doc.namespaces["soap"] == "http://schemas.xmlsoap.org/soap/envelope/"
    
    def test_parse_xml_with_default_namespace(self):
        """Test parsing XML with default namespace."""
        parser = XMLParser()
        xml_string = '<root xmlns="http://example.com/ns"><child>text</child></root>'
        
        doc = parser.parse_string(xml_string)
        
        assert "" in doc.namespaces
        assert doc.namespaces[""] == "http://example.com/ns"
        assert doc.root.namespace == "http://example.com/ns"
    
    def test_parse_empty_elements(self):
        """Test parsing XML with empty elements."""
        parser = XMLParser()
        xml_string = '<root><empty/><also_empty></also_empty></root>'
        
        doc = parser.parse_string(xml_string)
        
        assert len(doc.root.children) == 2
        assert doc.root.children[0].text is None
        assert doc.root.children[1].text is None
    
    def test_parse_nested_structure(self):
        """Test parsing deeply nested XML structure."""
        parser = XMLParser()
        xml_string = '''<root>
            <level1>
                <level2>
                    <level3>deep content</level3>
                </level2>
            </level1>
        </root>'''
        
        doc = parser.parse_string(xml_string)
        
        level1 = doc.root.children[0]
        level2 = level1.children[0]
        level3 = level2.children[0]
        
        assert level1.tag == "level1"
        assert level2.tag == "level2"
        assert level3.tag == "level3"
        assert level3.text == "deep content"


class TestXMLParserFileOperations:
    """Test file-based XML parsing."""
    
    def test_parse_existing_file(self, tmp_path):
        """Test parsing an existing XML file."""
        parser = XMLParser()
        
        # Create a temporary XML file
        xml_file = tmp_path / "test.xml"
        xml_file.write_text('<?xml version="1.0"?><root><child>content</child></root>')
        
        doc = parser.parse_file(xml_file)
        
        assert isinstance(doc, XMLDocument)
        assert doc.root.tag == "root"
        assert doc.root.children[0].text == "content"
    
    def test_parse_nonexistent_file(self):
        """Test parsing a file that doesn't exist raises FileNotFoundError."""
        parser = XMLParser()
        nonexistent_path = Path("/nonexistent/path/file.xml")
        
        with pytest.raises(FileNotFoundError):
            parser.parse_file(nonexistent_path)
    
    def test_parse_file_with_utf8_encoding(self, tmp_path):
        """Test parsing a file with UTF-8 encoding."""
        parser = XMLParser()
        
        # Create a file with UTF-8 content
        xml_file = tmp_path / "utf8.xml"
        xml_file.write_text(
            '<?xml version="1.0" encoding="UTF-8"?><root>Ñoño 中文 العربية</root>',
            encoding='utf-8'
        )
        
        doc = parser.parse_file(xml_file)
        
        assert doc.encoding == "UTF-8"
        assert "Ñoño" in doc.root.text
        assert "中文" in doc.root.text
    
    def test_parse_soap_sample_file(self):
        """Test parsing the actual SOAP sample file from the project."""
        parser = XMLParser()
        sample_file = Path("samples/uat-approved/R0001-approved.xml")
        
        # Skip if sample file doesn't exist
        if not sample_file.exists():
            pytest.skip("Sample file not found")
        
        doc = parser.parse_file(sample_file)
        
        # Verify SOAP structure
        assert doc.root.tag == "Envelope"
        assert "SOAP-ENV" in doc.namespaces
        assert doc.namespaces["SOAP-ENV"] == "http://schemas.xmlsoap.org/soap/envelope/"
        
        # Verify we can navigate the structure
        assert len(doc.root.children) >= 1


class TestXMLParserErrorHandling:
    """Test error handling in XML parsing."""
    
    def test_parse_invalid_xml_string(self):
        """Test parsing invalid XML raises XMLParseError."""
        parser = XMLParser()
        invalid_xml = "<root><unclosed>"
        
        with pytest.raises(XMLParseError) as exc_info:
            parser.parse_string(invalid_xml)
        
        assert "Invalid XML" in str(exc_info.value)
    
    def test_parse_malformed_xml_string(self):
        """Test parsing malformed XML raises XMLParseError."""
        parser = XMLParser()
        malformed_xml = "not xml at all"
        
        with pytest.raises(XMLParseError):
            parser.parse_string(malformed_xml)
    
    def test_parse_invalid_xml_file(self, tmp_path):
        """Test parsing a file with invalid XML raises XMLParseError."""
        parser = XMLParser()
        
        # Create a file with invalid XML
        xml_file = tmp_path / "invalid.xml"
        xml_file.write_text("<root><unclosed>")
        
        with pytest.raises(XMLParseError) as exc_info:
            parser.parse_file(xml_file)
        
        assert "Invalid XML" in str(exc_info.value)
    
    def test_parse_empty_string(self):
        """Test parsing an empty string raises XMLParseError."""
        parser = XMLParser()
        
        with pytest.raises(XMLParseError):
            parser.parse_string("")
    
    def test_parse_whitespace_only_string(self):
        """Test parsing whitespace-only string raises XMLParseError."""
        parser = XMLParser()
        
        with pytest.raises(XMLParseError):
            parser.parse_string("   \n\t  ")


class TestXMLParserNamespaceHandling:
    """Test namespace handling in XML parsing."""
    
    def test_multiple_namespace_declarations(self):
        """Test parsing XML with multiple namespace declarations."""
        parser = XMLParser()
        xml_string = '''<?xml version="1.0"?>
        <root xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
              xmlns:xsd="http://www.w3.org/2001/XMLSchema"
              xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <soap:body>content</soap:body>
        </root>'''
        
        doc = parser.parse_string(xml_string)
        
        assert "soap" in doc.namespaces
        assert "xsd" in doc.namespaces
        assert "xsi" in doc.namespaces
        assert doc.namespaces["soap"] == "http://schemas.xmlsoap.org/soap/envelope/"
        assert doc.namespaces["xsd"] == "http://www.w3.org/2001/XMLSchema"
    
    def test_namespace_on_elements(self):
        """Test that element namespaces are correctly extracted."""
        parser = XMLParser()
        xml_string = '''<root xmlns:ns="http://example.com">
            <ns:child>text</ns:child>
        </root>'''
        
        doc = parser.parse_string(xml_string)
        
        # The child element should have the namespace
        child = doc.root.children[0]
        assert child.namespace == "http://example.com"
        assert child.tag == "child"
    
    def test_preserve_namespace_prefixes(self):
        """Test that namespace prefixes are preserved in the namespace map."""
        parser = XMLParser()
        xml_string = '''<SOAP-ENV:Envelope 
            xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:m="http://wmworld/services">
            <SOAP-ENV:Body>
                <m:Response>data</m:Response>
            </SOAP-ENV:Body>
        </SOAP-ENV:Envelope>'''
        
        doc = parser.parse_string(xml_string)
        
        assert "SOAP-ENV" in doc.namespaces
        assert "m" in doc.namespaces
        assert doc.root.namespace == "http://schemas.xmlsoap.org/soap/envelope/"


class TestXMLParserTextHandling:
    """Test text content handling in XML parsing."""
    
    def test_whitespace_only_text_is_none(self):
        """Test that whitespace-only text content is treated as None."""
        parser = XMLParser()
        xml_string = '<root><child>   \n\t  </child></root>'
        
        doc = parser.parse_string(xml_string)
        
        assert doc.root.children[0].text is None
    
    def test_text_with_leading_trailing_whitespace(self):
        """Test that leading/trailing whitespace is stripped from text."""
        parser = XMLParser()
        xml_string = '<root><child>  text content  </child></root>'
        
        doc = parser.parse_string(xml_string)
        
        assert doc.root.children[0].text == "text content"
    
    def test_mixed_content_elements(self):
        """Test elements with both text and child elements."""
        parser = XMLParser()
        xml_string = '<root>text before<child>child text</child>text after</root>'
        
        doc = parser.parse_string(xml_string)
        
        # The root should have text content
        assert doc.root.text == "text before"
        # And should have a child
        assert len(doc.root.children) == 1
        assert doc.root.children[0].text == "child text"
