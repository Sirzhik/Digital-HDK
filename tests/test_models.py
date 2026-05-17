"""
Tests for Pydantic models in Digital SDK.
"""

import pytest
from src.digital.digital_hdk.models import Position, VisualElement, Wire, Circuit


class TestPosition:
    """Tests for Position class."""
    
    def test_position_creation(self):
        """Test creating a position."""
        pos = Position(x=520, y=380)
        assert pos.x == 520
        assert pos.y == 380
    
    def test_position_equality(self):
        """Test position equality."""
        pos1 = Position(x=520, y=380)
        pos2 = Position(x=520, y=380)
        pos3 = Position(x=520, y=381)
        
        assert pos1 == pos2
        assert pos1 != pos3
    
    def test_position_hashable(self):
        """Test using position in sets and dictionaries."""
        pos1 = Position(x=520, y=380)
        pos2 = Position(x=520, y=380)
        
        position_set = {pos1}
        assert pos2 in position_set
        
        position_dict = {pos1: "test"}
        assert position_dict[pos2] == "test"
    
    def test_position_repr(self):
        """Test string representation of position."""
        pos = Position(x=520, y=380)
        assert "520" in repr(pos)
        assert "380" in repr(pos)


class TestVisualElement:
    """Tests for VisualElement class."""
    
    def test_element_creation(self):
        """Test creating an element."""
        pos = Position(x=520, y=380)
        element = VisualElement(
            elementName="NAnd",
            pos=pos,
            elementAttributes={"Inputs": 3, "wideShape": True}
        )
        
        assert element.elementName == "NAnd"
        assert element.pos == pos
        assert element.elementAttributes["Inputs"] == 3
    
    def test_element_default_attributes(self):
        """Test default attribute values."""
        pos = Position(x=520, y=380)
        element = VisualElement(elementName="Led", pos=pos)
        
        assert element.elementAttributes == {}
        assert element.id is None
    
    def test_element_repr(self):
        """Test string representation of element."""
        pos = Position(x=520, y=380)
        element = VisualElement(elementName="NAnd", pos=pos)
        
        assert "NAnd" in repr(element)
        assert "520" in repr(element)


class TestWire:
    """Tests for Wire class."""
    
    def test_wire_creation(self):
        """Test creating a wire."""
        p1 = Position(x=620, y=400)
        p2 = Position(x=760, y=400)
        wire = Wire(p1=p1, p2=p2)
        
        assert wire.p1 == p1
        assert wire.p2 == p2
    
    def test_wire_is_valid(self):
        """Test wire validity."""
        p1 = Position(x=620, y=400)
        p2 = Position(x=760, y=400)
        same_pos = Position(x=620, y=400)
        
        valid_wire = Wire(p1=p1, p2=p2)
        invalid_wire = Wire(p1=p1, p2=same_pos)
        
        assert valid_wire.is_valid() is True
        assert invalid_wire.is_valid() is False
    
    def test_wire_repr(self):
        """Test string representation of wire."""
        p1 = Position(x=620, y=400)
        p2 = Position(x=760, y=400)
        wire = Wire(p1=p1, p2=p2)
        
        assert "620" in repr(wire)
        assert "760" in repr(wire)


class TestCircuit:
    """Tests for Circuit class."""
    
    def test_circuit_creation_default(self):
        """Test creating a circuit with default values."""
        circuit = Circuit()
        
        assert circuit.version == 2
        assert circuit.attributes == {}
        assert circuit.visualElements == []
        assert circuit.wires == []
        assert circuit.measurementOrdering == []
    
    def test_circuit_creation_with_data(self):
        """Test creating a circuit with data."""
        element = VisualElement(
            elementName="NAnd",
            pos=Position(x=520, y=380)
        )
        wire = Wire(p1=Position(x=620, y=400), p2=Position(x=760, y=400))
        
        circuit = Circuit(
            version=2,
            visualElements=[element],
            wires=[wire]
        )
        
        assert circuit.version == 2
        assert len(circuit.visualElements) == 1
        assert len(circuit.wires) == 1
    
    def test_circuit_repr(self):
        """Test string representation of circuit."""
        circuit = Circuit()
        
        assert "Circuit" in repr(circuit)
        assert "version=2" in repr(circuit)
