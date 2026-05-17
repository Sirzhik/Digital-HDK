

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class Position(BaseModel):
    """Coordinates of an element on the grid (units: 20 pixels)."""
    
    x: int  # X-coordinate
    y: int  # Y-coordinate
    
    def __hash__(self) -> int:
        """For use in sets and dictionaries."""
        return hash((self.x, self.y))
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Position):
            return NotImplemented
        return self.x == other.x and self.y == other.y
    
    def __lt__(self, other: 'Position') -> bool:
        """For comparing positions in min/max."""
        if not isinstance(other, Position):
            return NotImplemented
        if self.x != other.x:
            return self.x < other.x
        return self.y < other.y
    
    def __le__(self, other: 'Position') -> bool:
        if not isinstance(other, Position):
            return NotImplemented
        return self == other or self < other
    
    def __gt__(self, other: 'Position') -> bool:
        if not isinstance(other, Position):
            return NotImplemented
        return not self <= other
    
    def __ge__(self, other: 'Position') -> bool:
        if not isinstance(other, Position):
            return NotImplemented
        return not self < other
    
    def __repr__(self) -> str:
        return f"Position(x={self.x}, y={self.y})"


class VisualElement(BaseModel):
    """Represents a visual element in the circuit."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    elementName: str  # Component name (And, NAnd, In, Out, LED, etc.)
    pos: Position  # Placement coordinates {x, y}
    elementAttributes: Dict[str, Any] = Field(default_factory=dict)
    id: Optional[str] = None  # Unique identifier
    
    def __repr__(self) -> str:
        return f"VisualElement(name={self.elementName}, pos={self.pos})"


class Wire(BaseModel):
    """Connection between two ports."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    p1: Position  # First connection point
    p2: Position  # Second connection point
    
    def is_valid(self) -> bool:
        """Check that the points are different."""
        return self.p1 != self.p2
    
    def __repr__(self) -> str:
        return f"Wire(p1={self.p1}, p2={self.p2})"


class Circuit(BaseModel):
    """Complete representation of an electronic circuit."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    version: int = 2  # Format version (usually 2)
    attributes: Dict[str, str] = Field(default_factory=dict)  # Global circuit attributes
    visualElements: List[VisualElement] = Field(default_factory=list)  # All components
    wires: List[Wire] = Field(default_factory=list)  # All connections
    measurementOrdering: List[str] = Field(default_factory=list)  # Measurement signal ordering
    
    def __repr__(self) -> str:
        return f"Circuit(version={self.version}, elements={len(self.visualElements)}, wires={len(self.wires)})"
