"""
Tests for CircuitXMLParser.
"""

import pytest
from src.digital.digital_hdk.parser import CircuitXMLParser
from src.digital.digital_hdk.models import Circuit, Position, VisualElement, Wire
from src.digital.digital_hdk.exceptions import ParseError


class TestCircuitXMLParser:
    """Tests for XML parser."""
    
    def test_parse_simple_circuit(self):
        """Test parsing a simple circuit."""
        xml = """<?xml version="1.0" encoding="utf-8"?>
<circuit>
  <version>2</version>
  <attributes/>
  <visualElements/>
  <wires/>
  <measurementOrdering/>
</circuit>"""
        
        circuit = CircuitXMLParser.parse_xml(xml)
        
        assert circuit.version == 2
        assert circuit.visualElements == []
        assert circuit.wires == []
    
    def test_parse_circuit_with_elements(self):
        """Test parsing a circuit with elements."""
        xml = """<?xml version="1.0" encoding="utf-8"?>
<circuit>
  <version>2</version>
  <attributes/>
  <visualElements>
    <visualElement>
      <elementName>NAnd</elementName>
      <elementAttributes>
        <entry>
          <string>wideShape</string>
          <boolean>true</boolean>
        </entry>
        <entry>
          <string>Inputs</string>
          <int>3</int>
        </entry>
      </elementAttributes>
      <pos x="520" y="380"/>
    </visualElement>
    <visualElement>
      <elementName>LED</elementName>
      <elementAttributes>
        <entry>
          <string>Label</string>
          <string>Q</string>
        </entry>
      </elementAttributes>
      <pos x="980" y="400"/>
    </visualElement>
  </visualElements>
  <wires/>
  <measurementOrdering/>
</circuit>"""
        
        circuit = CircuitXMLParser.parse_xml(xml)
        
        assert len(circuit.visualElements) == 2
        assert circuit.visualElements[0].elementName == "NAnd"
        assert circuit.visualElements[0].pos.x == 520
        assert circuit.visualElements[0].elementAttributes["Inputs"] == 3
        assert circuit.visualElements[0].elementAttributes["wideShape"] is True
        assert circuit.visualElements[1].elementName == "LED"
        assert circuit.visualElements[1].elementAttributes["Label"] == "Q"
    
    def test_parse_circuit_with_wires(self):
        """Test parsing a circuit with wires."""
        xml = """<?xml version="1.0" encoding="utf-8"?>
<circuit>
  <version>2</version>
  <attributes/>
  <visualElements/>
  <wires>
    <wire>
      <p1 x="620" y="400"/>
      <p2 x="760" y="400"/>
    </wire>
    <wire>
      <p1 x="460" y="400"/>
      <p2 x="520" y="400"/>
    </wire>
  </wires>
  <measurementOrdering/>
</circuit>"""
        
        circuit = CircuitXMLParser.parse_xml(xml)
        
        assert len(circuit.wires) == 2
        assert circuit.wires[0].p1.x == 620
        assert circuit.wires[0].p2.x == 760
        assert circuit.wires[1].p1.x == 460
        assert circuit.wires[1].p2.x == 520
    
    def test_parse_invalid_xml(self):
        """Test parsing invalid XML."""
        invalid_xml = "<circuit><version>2</version>"  # Unclosed XML
        
        with pytest.raises(ParseError):
            CircuitXMLParser.parse_xml(invalid_xml)
    
    def test_parse_wrong_root_element(self):
        """Test parsing with wrong root element."""
        xml = """<?xml version="1.0" encoding="utf-8"?>
<wrong_root>
  <version>2</version>
</wrong_root>"""
        
        with pytest.raises(ParseError):
            CircuitXMLParser.parse_xml(xml)
    
    def test_to_xml_simple_circuit(self):
        """Test serializing a simple circuit to XML."""
        circuit = Circuit(version=2)
        xml = CircuitXMLParser.to_xml(circuit)
        
        assert '<?xml version' in xml
        assert '<circuit>' in xml
        assert '<version>2</version>' in xml
        assert '<visualElements/>' in xml or '<visualElements></visualElements>' in xml
    
    def test_to_xml_with_elements(self):
        """Test serializing a circuit with elements to XML."""
        element = VisualElement(
            elementName="NAnd",
            pos=Position(x=520, y=380),
            elementAttributes={"Inputs": 3, "wideShape": True}
        )
        circuit = Circuit(visualElements=[element])
        xml = CircuitXMLParser.to_xml(circuit)
        
        assert '<elementName>NAnd</elementName>' in xml
        assert 'x="520"' in xml
        assert 'y="380"' in xml
        assert '<int>3</int>' in xml
        assert '<boolean>true</boolean>' in xml
    
    def test_to_xml_with_wires(self):
        """Test serializing a circuit with wires to XML."""
        wire = Wire(p1=Position(x=620, y=400), p2=Position(x=760, y=400))
        circuit = Circuit(wires=[wire])
        xml = CircuitXMLParser.to_xml(circuit)
        
        assert '<wire>' in xml
        assert 'x="620"' in xml
        assert 'x="760"' in xml
    
    def test_roundtrip_parse_and_serialize(self):
        """Test roundtrip parsing and serialization."""
        # Create circuit
        element1 = VisualElement(
            elementName="NAnd",
            pos=Position(x=520, y=380),
            elementAttributes={"Inputs": 3}
        )
        element2 = VisualElement(
            elementName="LED",
            pos=Position(x=980, y=400),
            elementAttributes={"Label": "Q"}
        )
        wire = Wire(p1=Position(x=620, y=400), p2=Position(x=760, y=400))
        
        original_circuit = Circuit(
            visualElements=[element1, element2],
            wires=[wire]
        )
        
        # Serialize to XML
        xml = CircuitXMLParser.to_xml(original_circuit)
        
        # Parse back
        parsed_circuit = CircuitXMLParser.parse_xml(xml)
        
        # Verify correspondence
        assert len(parsed_circuit.visualElements) == 2
        assert parsed_circuit.visualElements[0].elementName == "NAnd"
        assert parsed_circuit.visualElements[1].elementName == "LED"
        assert len(parsed_circuit.wires) == 1
        assert parsed_circuit.wires[0].p1.x == 620
