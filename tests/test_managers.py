"""
Tests for managers (CircuitManager, ElementManager, WireManager).
"""

import pytest
import tempfile
from pathlib import Path

from src.digital.digital_hdk.managers import CircuitManager, ElementManager, WireManager
from src.digital.digital_hdk.models import Circuit, Position, VisualElement, Wire
from src.digital.digital_hdk.exceptions import (
    PositionOccupiedError,
    InvalidElementError,
    InvalidWireError,
    WireAlreadyExists,
    ParseError,
    ValidationError,
)


class TestElementManager:
    """Tests for ElementManager."""
    
    def test_place_element(self):
        """Test placing an element."""
        circuit = Circuit()
        mgr = ElementManager(circuit)
        
        element = mgr.place("NAnd", Position(x=520, y=380), {"Inputs": 3})
        
        assert element.elementName == "NAnd"
        assert element.pos.x == 520
        assert element.pos.y == 380
        assert element.elementAttributes["Inputs"] == 3
        assert len(circuit.visualElements) == 1
    
    def test_place_element_duplicate_position(self):
        """Test error when placing at an occupied position."""
        circuit = Circuit()
        mgr = ElementManager(circuit)
        
        mgr.place("NAnd", Position(x=520, y=380))
        
        with pytest.raises(PositionOccupiedError):
            mgr.place("And", Position(x=520, y=380))
    
    def test_place_invalid_element(self):
        """Test error when placing an unknown component."""
        circuit = Circuit()
        mgr = ElementManager(circuit)
        
        with pytest.raises(InvalidElementError):
            mgr.place("UnknownElement", Position(x=520, y=380))
    
    def test_get_element(self):
        """Test getting an element by position."""
        circuit = Circuit()
        mgr = ElementManager(circuit)
        
        placed = mgr.place("NAnd", Position(x=520, y=380))
        retrieved = mgr.get(Position(x=520, y=380))
        
        assert retrieved is not None
        assert retrieved.elementName == placed.elementName
    
    def test_get_nonexistent_element(self):
        """Test getting a non-existent element."""
        circuit = Circuit()
        mgr = ElementManager(circuit)
        
        result = mgr.get(Position(x=520, y=380))
        
        assert result is None
    
    def test_list_all_elements(self):
        """Test getting a list of all elements."""
        circuit = Circuit()
        mgr = ElementManager(circuit)
        
        mgr.place("NAnd", Position(x=520, y=380))
        mgr.place("LED", Position(x=980, y=400))
        
        all_elements = mgr.list_all()
        
        assert len(all_elements) == 2
        assert all_elements[0].elementName == "NAnd"
        assert all_elements[1].elementName == "LED"
    
    def test_remove_element(self):
        """Test removing an element."""
        circuit = Circuit()
        mgr = ElementManager(circuit)
        
        mgr.place("NAnd", Position(x=520, y=380))
        result = mgr.remove(Position(x=520, y=380))
        
        assert result is True
        assert len(circuit.visualElements) == 0
    
    def test_remove_nonexistent_element(self):
        """Test removing a non-existent element."""
        circuit = Circuit()
        mgr = ElementManager(circuit)
        
        result = mgr.remove(Position(x=520, y=380))
        
        assert result is False
    
    def test_remove_element_removes_wires(self):
        """Test that removing an element removes associated wires."""
        circuit = Circuit()
        elem_mgr = ElementManager(circuit)
        wire_mgr = WireManager(circuit)
        
        elem_mgr.place("NAnd", Position(x=520, y=380))
        elem_mgr.place("LED", Position(x=980, y=400))
        wire_mgr.connect(Position(x=520, y=380), Position(x=980, y=400))
        
        assert len(circuit.wires) == 1
        
        elem_mgr.remove(Position(x=520, y=380))
        
        assert len(circuit.wires) == 0
    
    def test_update_attributes(self):
        """Test updating element attributes."""
        circuit = Circuit()
        mgr = ElementManager(circuit)
        
        mgr.place("NAnd", Position(x=520, y=380), {"Inputs": 2})
        result = mgr.update_attributes(Position(x=520, y=380), {"Inputs": 3})
        
        assert result is True
        element = mgr.get(Position(x=520, y=380))
        assert element.elementAttributes["Inputs"] == 3
    
    def test_update_nonexistent_element_attributes(self):
        """Test updating attributes of a non-existent element."""
        circuit = Circuit()
        mgr = ElementManager(circuit)
        
        result = mgr.update_attributes(Position(x=520, y=380), {"Inputs": 3})
        
        assert result is False


class TestWireManager:
    """Tests for WireManager."""
    
    def test_connect_wires(self):
        """Test connecting wires."""
        circuit = Circuit()
        mgr = WireManager(circuit)
        
        wire = mgr.connect(Position(x=620, y=400), Position(x=760, y=400))
        
        assert wire.p1.x == 620
        assert wire.p2.x == 760
        assert len(circuit.wires) == 1
    
    def test_connect_same_position(self):
        """Test error when connecting wire to the same position."""
        circuit = Circuit()
        mgr = WireManager(circuit)
        
        with pytest.raises(InvalidWireError):
            mgr.connect(Position(x=620, y=400), Position(x=620, y=400))
    
    def test_connect_duplicate_wire(self):
        """Test error when creating a duplicate wire."""
        circuit = Circuit()
        mgr = WireManager(circuit)
        
        mgr.connect(Position(x=620, y=400), Position(x=760, y=400))
        
        with pytest.raises(WireAlreadyExists):
            mgr.connect(Position(x=620, y=400), Position(x=760, y=400))
    
    def test_connect_duplicate_wire_reversed(self):
        """Test error when creating a wire in the reverse direction."""
        circuit = Circuit()
        mgr = WireManager(circuit)
        
        mgr.connect(Position(x=620, y=400), Position(x=760, y=400))
        
        # Wires are equivalent in both directions
        with pytest.raises(WireAlreadyExists):
            mgr.connect(Position(x=760, y=400), Position(x=620, y=400))
    
    def test_disconnect_wire(self):
        """Test removing a wire."""
        circuit = Circuit()
        mgr = WireManager(circuit)
        
        mgr.connect(Position(x=620, y=400), Position(x=760, y=400))
        result = mgr.disconnect(Position(x=620, y=400), Position(x=760, y=400))
        
        assert result is True
        assert len(circuit.wires) == 0
    
    def test_disconnect_nonexistent_wire(self):
        """Test removing a non-existent wire."""
        circuit = Circuit()
        mgr = WireManager(circuit)
        
        result = mgr.disconnect(Position(x=620, y=400), Position(x=760, y=400))
        
        assert result is False
    
    def test_get_wires_from_position(self):
        """Test getting wires from a position."""
        circuit = Circuit()
        mgr = WireManager(circuit)
        
        p1 = Position(x=620, y=400)
        p2 = Position(x=760, y=400)
        p3 = Position(x=900, y=400)
        
        mgr.connect(p1, p2)
        mgr.connect(p1, p3)
        
        wires = mgr.get_wires_from(p1)
        
        assert len(wires) == 2
    
    def test_get_all_wires(self):
        """Test getting all wires."""
        circuit = Circuit()
        mgr = WireManager(circuit)
        
        mgr.connect(Position(x=620, y=400), Position(x=760, y=400))
        mgr.connect(Position(x=460, y=400), Position(x=520, y=400))
        
        wires = mgr.get_all_wires()
        
        assert len(wires) == 2
    
    def test_validate_wires_valid(self):
        """Test validating valid wires."""
        circuit = Circuit()
        mgr = WireManager(circuit)
        
        mgr.connect(Position(x=620, y=400), Position(x=760, y=400))
        
        errors = mgr.validate_wires()
        
        assert len(errors) == 0
    
    def test_validate_wires_invalid(self):
        """Test validating invalid wires."""
        circuit = Circuit()
        mgr = WireManager(circuit)
        
        # Manually add invalid wire (for testing)
        invalid_wire = Wire(p1=Position(x=620, y=400), p2=Position(x=620, y=400))
        circuit.wires.append(invalid_wire)
        
        errors = mgr.validate_wires()
        
        assert len(errors) > 0


class TestCircuitManager:
    """Tests for CircuitManager."""
    
    def test_create_new_circuit(self):
        """Test creating a new circuit."""
        mgr = CircuitManager()
        
        assert mgr.circuit is not None
        assert isinstance(mgr.circuit, Circuit)
        assert mgr.elements is not None
        assert mgr.wires is not None
    
    def test_place_and_connect(self):
        """Test placing and connecting elements."""
        mgr = CircuitManager()
        
        mgr.elements.place("NAnd", Position(x=520, y=380), {"Inputs": 3})
        mgr.elements.place("LED", Position(x=980, y=400), {"Label": "Q"})
        mgr.wires.connect(Position(x=520, y=380), Position(x=980, y=400))
        
        assert len(mgr.elements.list_all()) == 2
        assert len(mgr.wires.get_all_wires()) == 1
    
    def test_save_and_load_circuit(self):
        """Test saving and loading a circuit."""
        # Create circuit
        mgr = CircuitManager()
        mgr.elements.place("NAnd", Position(x=520, y=380), {"Inputs": 3})
        mgr.elements.place("LED", Position(x=980, y=400), {"Label": "Q"})
        mgr.wires.connect(Position(x=620, y=400), Position(x=760, y=400))
        
        # Save to temporary file
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test_circuit.dig"
            mgr.save(str(filepath))
            
            # Load back
            loaded_mgr = CircuitManager(str(filepath))
            
            # Verify correspondence
            assert len(loaded_mgr.elements.list_all()) == 2
            assert len(loaded_mgr.wires.get_all_wires()) == 1
    
    def test_load_nonexistent_file(self):
        """Test loading a non-existent file."""
        with pytest.raises(ParseError):
            CircuitManager("/nonexistent/path/to/circuit.dig")
    
    def test_validate_circuit(self):
        """Test validating a circuit."""
        mgr = CircuitManager()
        
        mgr.elements.place("NAnd", Position(x=520, y=380))
        mgr.elements.place("LED", Position(x=980, y=400))
        
        errors = mgr.validate()
        
        assert len(errors) == 0
    
    def test_validate_circuit_with_duplicate_position(self):
        """Test validating a circuit with duplicate positions."""
        mgr = CircuitManager()
        
        # Manually add elements with the same position
        pos = Position(x=520, y=380)
        mgr.circuit.visualElements.append(
            VisualElement(elementName="NAnd", pos=pos)
        )
        mgr.circuit.visualElements.append(
            VisualElement(elementName="LED", pos=pos)
        )
        
        errors = mgr.validate()
        
        assert len(errors) > 0


class TestCircuitManagerIntegration:
    """Integration tests for CircuitManager."""
    
    def test_load_jk_dig(self):
        """Test loading existing JK.dig file."""
        try:
            mgr = CircuitManager("tests/data/JK.dig")
            
            assert len(mgr.elements.list_all()) > 0
            assert len(mgr.wires.get_all_wires()) > 0
            
            # Validate circuit
            errors = mgr.validate()
            assert len(errors) == 0
        except FileNotFoundError:
            pytest.skip("JK.dig file not found")
    
    def test_load_and_save_jk_dig_copy(self):
        """Test loading JK.dig, saving a copy and reloading."""
        try:
            original_mgr = CircuitManager("tests/data/JK.dig")
            original_elements = len(original_mgr.elements.list_all())
            original_wires = len(original_mgr.wires.get_all_wires())
            
            with tempfile.TemporaryDirectory() as tmpdir:
                filepath = Path(tmpdir) / "JK_copy.dig"
                original_mgr.save(str(filepath))
                
                # Load copy
                copy_mgr = CircuitManager(str(filepath))
                
                assert len(copy_mgr.elements.list_all()) == original_elements
                assert len(copy_mgr.wires.get_all_wires()) == original_wires
        except FileNotFoundError:
            pytest.skip("JK.dig file not found")
