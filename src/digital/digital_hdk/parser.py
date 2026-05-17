"""
XML parser for transforming XML to Pydantic models and vice versa.
"""

from typing import Any, Dict
import lxml.etree as ET

from .models import Circuit, VisualElement, Wire, Position
from .exceptions import ParseError


class CircuitXMLParser:
    """Parses XML from .dig files to Pydantic models."""
    
    # Known Digital components
    KNOWN_ELEMENTS = {
        # Logic
        "And", "NAnd", "Or", "NOr", "XOr", "XNOr", "Not", "LookUpTable",
        # IO
        "In", "Out", "Clock", "LED", "RGBLED", "Button", "DipSwitch", "PolarityAwareLED",
        # Plexers
        "Multiplexer", "Demultiplexer", "Decoder", "PriorityEncoder",
        # Memory
        "FlipFlop", "DRAM", "ROM", "RAM",
        # Arithmetic
        "Add", "Sub", "Mul", "Div", "Comparator",
        # Additional
        "Const", "Splitter", "Merge", "BitExtractor", "Tunnel"
    }
    
    @staticmethod
    def parse_xml(xml_content: str) -> Circuit:
        """Transform XML string to Circuit object.
        
        Args:
            xml_content: Content of the XML file
        
        Returns:
            Circuit object
        
        Raises:
            ParseError: If XML is invalid
        """
        try:
            root = ET.fromstring(xml_content.encode('utf-8'))
        except ET.XMLSyntaxError as e:
            raise ParseError(f"XML parsing error: {e}")
        
        if root.tag != "circuit":
            raise ParseError("Root element must be <circuit>")
        
        # Parse version
        version_elem = root.find("version")
        version = int(version_elem.text) if version_elem is not None and version_elem.text else 2
        
        # Parse global attributes
        attributes = CircuitXMLParser._parse_attributes(root.find("attributes"))
        
        # Parse visual elements
        visual_elements = []
        ve_container = root.find("visualElements")
        if ve_container is not None:
            for ve_elem in ve_container.findall("visualElement"):
                element = CircuitXMLParser._parse_visual_element(ve_elem)
                visual_elements.append(element)
        
        # Parse wires
        wires = []
        wires_container = root.find("wires")
        if wires_container is not None:
            for wire_elem in wires_container.findall("wire"):
                wire = CircuitXMLParser._parse_wire(wire_elem)
                wires.append(wire)
        
        # Parse measurementOrdering
        measurement_ordering = []
        mo_container = root.find("measurementOrdering")
        if mo_container is not None:
            for entry in mo_container.findall("entry"):
                text_elem = entry.find("string")
                if text_elem is not None and text_elem.text:
                    measurement_ordering.append(text_elem.text)
        
        return Circuit(
            version=version,
            attributes=attributes,
            visualElements=visual_elements,
            wires=wires,
            measurementOrdering=measurement_ordering
        )
    
    @staticmethod
    def _parse_attributes(attributes_elem: Any) -> Dict[str, str]:
        """Parse global circuit attributes."""
        attributes = {}
        if attributes_elem is None:
            return attributes
        
        for entry in attributes_elem.findall("entry"):
            key_elem = entry.find("string")
            value_elem = entry.find("string[2]")
            
            # Can be a pair string/string or other combinations
            strings = entry.findall("string")
            if len(strings) >= 2:
                key = strings[0].text
                value = strings[1].text
                if key:
                    attributes[key] = value or ""
        
        return attributes
    
    @staticmethod
    def _parse_visual_element(ve_elem: Any) -> VisualElement:
        """Parse a visual element."""
        element_name_elem = ve_elem.find("elementName")
        element_name = element_name_elem.text if element_name_elem is not None else ""
        
        # Parse position
        pos_elem = ve_elem.find("pos")
        x = int(pos_elem.get("x", 0)) if pos_elem is not None else 0
        y = int(pos_elem.get("y", 0)) if pos_elem is not None else 0
        pos = Position(x=x, y=y)
        
        # Parse element attributes
        element_attributes = {}
        ea_container = ve_elem.find("elementAttributes")
        if ea_container is not None:
            element_attributes = CircuitXMLParser._parse_element_attributes(ea_container)
        
        return VisualElement(
            elementName=element_name,
            pos=pos,
            elementAttributes=element_attributes
        )
    
    @staticmethod
    def _parse_element_attributes(ea_container: Any) -> Dict[str, Any]:
        """Parse element attributes with type casting."""
        attributes = {}
        
        for entry in ea_container.findall("entry"):
            key_elem = entry.find("string")
            if key_elem is None:
                continue
            
            key = key_elem.text
            if not key:
                continue
            
            # Determine value type
            value = None
            
            if entry.find("int") is not None:
                int_elem = entry.find("int")
                value = int(int_elem.text) if int_elem.text else 0
            elif entry.find("boolean") is not None:
                bool_elem = entry.find("boolean")
                value = bool_elem.text == "true" if bool_elem.text else False
            elif entry.find("string") is not None:
                # Look for the second string element (first is the key)
                strings = entry.findall("string")
                if len(strings) > 1:
                    value = strings[1].text or ""
                else:
                    value = ""
            elif entry.find("hex") is not None:
                hex_elem = entry.find("hex")
                value = hex_elem.text or ""
            
            if value is not None:
                attributes[key] = value
        
        return attributes
    
    @staticmethod
    def _parse_wire(wire_elem: Any) -> Wire:
        """Parse a wire."""
        p1_elem = wire_elem.find("p1")
        p2_elem = wire_elem.find("p2")
        
        p1_x = int(p1_elem.get("x", 0)) if p1_elem is not None else 0
        p1_y = int(p1_elem.get("y", 0)) if p1_elem is not None else 0
        p1 = Position(x=p1_x, y=p1_y)
        
        p2_x = int(p2_elem.get("x", 0)) if p2_elem is not None else 0
        p2_y = int(p2_elem.get("y", 0)) if p2_elem is not None else 0
        p2 = Position(x=p2_x, y=p2_y)
        
        return Wire(p1=p1, p2=p2)
    
    @staticmethod
    def to_xml(circuit: Circuit) -> str:
        """Transform Circuit object to XML string.
        
        Args:
            circuit: Circuit object
        
        Returns:
            Formatted XML string
        """
        # Create root element
        root = ET.Element("circuit")
        
        # Add version
        version_elem = ET.SubElement(root, "version")
        version_elem.text = str(circuit.version)
        
        # Add attributes
        attributes_elem = ET.SubElement(root, "attributes")
        for key, value in circuit.attributes.items():
            entry = ET.SubElement(attributes_elem, "entry")
            key_elem = ET.SubElement(entry, "string")
            key_elem.text = key
            val_elem = ET.SubElement(entry, "string")
            val_elem.text = str(value)
        
        # Add visual elements
        visual_elements_elem = ET.SubElement(root, "visualElements")
        for element in circuit.visualElements:
            ve_elem = ET.SubElement(visual_elements_elem, "visualElement")
            
            name_elem = ET.SubElement(ve_elem, "elementName")
            name_elem.text = element.elementName
            
            # Add element attributes
            if element.elementAttributes:
                ea_elem = ET.SubElement(ve_elem, "elementAttributes")
                CircuitXMLParser._serialize_attributes(ea_elem, element.elementAttributes)
            else:
                ET.SubElement(ve_elem, "elementAttributes")
            
            # Add position
            pos_elem = ET.SubElement(ve_elem, "pos")
            pos_elem.set("x", str(element.pos.x))
            pos_elem.set("y", str(element.pos.y))
        
        # Add wires
        wires_elem = ET.SubElement(root, "wires")
        for wire in circuit.wires:
            wire_elem = ET.SubElement(wires_elem, "wire")
            
            p1_elem = ET.SubElement(wire_elem, "p1")
            p1_elem.set("x", str(wire.p1.x))
            p1_elem.set("y", str(wire.p1.y))
            
            p2_elem = ET.SubElement(wire_elem, "p2")
            p2_elem.set("x", str(wire.p2.x))
            p2_elem.set("y", str(wire.p2.y))
        
        # Add measurementOrdering
        mo_elem = ET.SubElement(root, "measurementOrdering")
        for measurement in circuit.measurementOrdering:
            entry = ET.SubElement(mo_elem, "entry")
            entry_text = ET.SubElement(entry, "string")
            entry_text.text = measurement
        
        # Format XML with indentation
        ET.indent(root, space="  ")
        
        # Return string with XML declaration
        xml_bytes = ET.tostring(root, encoding='utf-8', xml_declaration=True)
        return xml_bytes.decode('utf-8')
    
    @staticmethod
    def _serialize_attributes(ea_elem: Any, attributes: Dict[str, Any]) -> None:
        """Serialize element attributes while preserving types."""
        for key, value in attributes.items():
            entry = ET.SubElement(ea_elem, "entry")
            
            key_elem = ET.SubElement(entry, "string")
            key_elem.text = key
            
            # Determine value type and add corresponding element
            if isinstance(value, bool):
                val_elem = ET.SubElement(entry, "boolean")
                val_elem.text = "true" if value else "false"
            elif isinstance(value, int):
                val_elem = ET.SubElement(entry, "int")
                val_elem.text = str(value)
            else:
                val_elem = ET.SubElement(entry, "string")
                val_elem.text = str(value)
