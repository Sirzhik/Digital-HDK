"""
Manager for handling with circuts, elements and wires. 
This is the main interface for users to interact with the circuit data structure
"""

from typing import Dict, List, Optional, Any
from pathlib import Path

from .models import Circuit, VisualElement, Wire, Position
from .parser import CircuitXMLParser
from .exceptions import (
    PositionOccupiedError,
    InvalidElementError,
    InvalidWireError,
    WireAlreadyExists,
    ParseError
)


class ElementManager:
    """Class controls placement, retrieval and management of components in the circuit."""
    
    # Known components
    KNOWN_ELEMENTS = {
        # Logic
        "And", "NAnd", "Or", "NOr", "XOr", "XNOr", "Not", "LookUpTable",
        # IO
        "In", "Out", "Clock", "LED", "RGBLED", "Button", "DipSwitch", "Probe", "Out",
        # Plexers
        "Multiplexer", "Demultiplexer", "Decoder", "BitSelector", "PriorityEncoder",
        # Flip-Flops
        "D_FF", "T_FF", "JK_FF", "RS_FF_AS", "RS_FF", "D_FF_AS", "Monoflop",
        # Memory
        "Register", "ROMDualPort", "ROM", "RAM", "Counter", "CounterPreset", "PRNG",
        "EEPROM", "EEPROM", "RAMDualPort", "BlockRANDualPort", "RAMSinglePort", "RAMSinglePortSel",
        "RegisterFile", "RAMDualAccess", "RAMDualAccess", "RAMSingleAccess", "RAMsync", "GraphicCard",
        # Arithmetic
        "Add", "Sub", "Mul", "Div", "Comparator",
        # Additional
        "Const", "Splitter", "Merge", "BitExtractor", "Tunnel"
    }
    
    def __init__(self, circuit: Circuit):
        """
        Args:
            circuit: Object of Circuit to manage
        """
        self.circuit = circuit
        self._rebuild_registry()
    
    def _rebuild_registry(self) -> None:
        """Rebuild the element registry based on positions."""
        self._position_map: Dict[Position, VisualElement] = {}
        for element in self.circuit.visualElements:
            self._position_map[element.pos] = element
    
    def place(self,
              element_name: str,
              position: Position,
              attributes: Optional[Dict[str, Any]] = None) -> VisualElement:
        """Place an element at the specified position

        Args:
            element_name: Component name (And, NAnd, In, Out, LED etc.)
            position: Position on the grid (x, y coordinates)
            attributes: Component attributes (Inputs=3, Label="J", Bits=8 etc.)
        
        Returns:
            Created VisualElement
        
        Raises:
            PositionOccupiedError: If the position is already occupied by another component
            InvalidElementError: If the component name is not known
        """
        # Validate the component name
        if element_name not in self.KNOWN_ELEMENTS:
            raise InvalidElementError(
                f"Unknown component: {element_name}. "
                f"Available components: {', '.join(sorted(self.KNOWN_ELEMENTS))}"
            )
        
        # Check if the position is already occupied
        if position in self._position_map:
            raise PositionOccupiedError(
                f"Position {position} is already occupied by component {self._position_map[position].elementName}"
            )
        
        # Normalize the attributes
        normalized_attributes = attributes or {}
        
        # Create the element
        element = VisualElement(
            elementName=element_name,
            pos=position,
            elementAttributes=normalized_attributes
        )
        
        # Add to the circuit and registry
        self.circuit.visualElements.append(element)
        self._position_map[position] = element
        
        return element
    
    def remove(self, position: Position) -> bool:
        """Remove an element at the specified position.
        
        Args:
            position: Position of the element
        
        Returns:
            True if the element was removed, False if the element was not found
        
        Note:
            Removal automatically removes all connections,
            connected to the component.
        """
        if position not in self._position_map:
            return False
        
        element = self._position_map[position]
        
        # Remove from visualElements
        self.circuit.visualElements.remove(element)
        
        # Remove all connections, connected to this element
        # (this will be done in WireManager when removing the element)
        wires_to_remove = [
            wire for wire in self.circuit.wires
            if wire.p1 == position or wire.p2 == position
        ]
        for wire in wires_to_remove:
            self.circuit.wires.remove(wire)
        
        # Update the registry
        del self._position_map[position]
        
        return True
    
    def get(self, position: Position) -> Optional[VisualElement]:
        """Get an element at the specified position.
        
        Args:
            position: Position of the element
        
        Returns:
            VisualElement or None
        """
        return self._position_map.get(position)
    
    def list_all(self) -> List[VisualElement]:
        """Get a list of all components."""
        return self.circuit.visualElements.copy()
    
    def update_attributes(self,
                         position: Position,
                         attributes: Dict[str, Any]) -> bool:
        """Update the attributes of a component (e.g., Label, Inputs).
        
        Args:
            position: Position of the element
            attributes: New attributes
        
        Returns:
            True if updated, False if the element was not found
        """
        element = self.get(position)
        if element is None:
            return False
        
        element.elementAttributes.update(attributes)
        return True


class WireManager:
    """Controls creation, retrieval and management of wires in the circuit."""
    
    def __init__(self, circuit: Circuit):
        """Initialize the wire manager.
        
        Args:
            circuit: Circuit manage object
        """
        self.circuit = circuit
    
    def connect(self, p1: Position, p2: Position) -> Wire:
        """Create a wire between two positions.
        
        Args:
            p1: First connection point
            p2: Second connection point
        
        Returns:
            Created wire
        
        Raises:
            InvalidWireError: If the wire is invalid (points are the same, etc.)
            WireAlreadyExists: If a wire between these points already exists
        """
        # Validate the wire
        if p1 == p2:
            raise InvalidWireError(f"Wire cannot connect a point to itself: {p1}")
        
        # Check if a wire between these points already exists
        # (wire can be in either direction, so we check both)
        for existing_wire in self.circuit.wires:
            if (existing_wire.p1 == p1 and existing_wire.p2 == p2) or \
               (existing_wire.p1 == p2 and existing_wire.p2 == p1):
                raise WireAlreadyExists(
                    f"Wire between {p1} and {p2} already exists"
                )
        
        # Create the wire
        wire = Wire(p1=p1, p2=p2)
        
        # Add to the circuit
        self.circuit.wires.append(wire)
        
        return wire
    
    def disconnect(self, p1: Position, p2: Position) -> bool:
        """Remove a wire between two positions.
        
        Args:
            p1: First connection point
            p2: Second connection point
        
        Returns:
            True if removed, False if the connection did not exist
        """
        wire_to_remove = None
        
        for wire in self.circuit.wires:
            if (wire.p1 == p1 and wire.p2 == p2) or \
               (wire.p1 == p2 and wire.p2 == p1):
                wire_to_remove = wire
                break
        
        if wire_to_remove is None:
            return False
        
        self.circuit.wires.remove(wire_to_remove)
        return True
    
    def get_wires_from(self, position: Position) -> List[Wire]:
        """Get all wires connected to a position.
        
        Args:
            position: Position
        
        Returns:
            List of wires that have p1 or p2 containing this position
        """
        return [
            wire for wire in self.circuit.wires
            if wire.p1 == position or wire.p2 == position
        ]
    
    def get_all_wires(self) -> List[Wire]:
        """Get all wires in the circuit."""
        return self.circuit.wires.copy()
    
    def validate_wires(self) -> List[str]:
        """Validate the integrity of all connections.
        
        Returns:
            List of validation errors (empty if all is OK)
        
        Errors may include:
            - "Wire connects to empty space"
            - "Duplicate wire detected"
            - "Invalid wire coordinates"
        """
        errors = []
        seen_wires = set()
        
        for idx, wire in enumerate(self.circuit.wires):
            # Check if the wire connects to valid positions (not negative, etc.)
            if not wire.is_valid():
                errors.append(
                    f"Wire[{idx}]: Wire connects to empty space: {wire.p1}"
                )
            
            # Check for duplicates (normalize order)
            wire_key = (min(wire.p1, wire.p2), max(wire.p1, wire.p2))
            if wire_key in seen_wires:
                errors.append(
                    f"Wire[{idx}]: Duplicate wire detected: {wire.p1} <-> {wire.p2}"
                )
            seen_wires.add(wire_key)
        
        return errors


class CircuitManager:
    """Manages the full lifecycle of a .dig file."""
    
    def __init__(self, filepath: Optional[str] = None):
        """Initialize the circuit manager.
        
        Args:
            filepath: Path to the existing .dig file (optional)
        """
        if filepath:
            self.circuit = self.load(filepath)
        else:
            self.circuit = Circuit()
        
        self.elements = ElementManager(self.circuit)
        self.wires = WireManager(self.circuit)
        self._filepath = filepath
    
    def load(self, filepath: str) -> Circuit:
        """Load a circuit from a .dig file.
        
        Args:
            filepath: Path to the .dig file
        
        Returns:
            Loaded Circuit object
        
        Raises:
            ParseError: If the file cannot be read or parsed
        """
        try:
            path = Path(filepath)
            if not path.exists():
                raise ParseError(f"File does not exist: {filepath}")
            
            with open(path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            
            circuit = CircuitXMLParser.parse_xml(xml_content)
            self._filepath = filepath
            return circuit
        
        except ParseError:
            raise
        except Exception as e:
            raise ParseError(f"Error occurred while loading file {filepath}: {e}")
    
    def save(self, filepath: str) -> None:
        """Save the circuit to a .dig file.
        
        Args:
            filepath: Path for saving the file
        
        Raises:
            Exception: If the file cannot be saved
        """
        try:
            xml_content = CircuitXMLParser.to_xml(self.circuit)
            path = Path(filepath)
            
            # Create parent directories if they do not exist
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            
            self._filepath = filepath
        except Exception as e:
            raise Exception(f"Error occurred while saving file {filepath}: {e}")
    
    def validate(self) -> List[str]:
        """Validate the entire circuit.
        
        Returns:
            List of validation errors (empty if all is OK)
        """
        errors = []
        
        # Validate wires
        wire_errors = self.wires.validate_wires()
        errors.extend(wire_errors)
        
        # Check for elements at the same position
        positions = {}
        for element in self.circuit.visualElements:
            if element.pos in positions:
                errors.append(
                    f"Two elements at the same position {element.pos}: "
                    f"{positions[element.pos].elementName} and {element.elementName}"
                )
            positions[element.pos] = element
        
        return errors
