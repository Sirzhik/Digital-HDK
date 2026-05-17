"""
Digital HDK - software interface for working with .dig files.
"""

from .models import Circuit, VisualElement, Wire, Position
from .managers import CircuitManager, ElementManager, WireManager
from .parser import CircuitXMLParser
from .exceptions import (
    DigitalHDKError,
    PositionOccupiedError,
    InvalidElementError,
    InvalidWireError,
    WireAlreadyExists,
    ParseError,
    ValidationError,
)

__version__ = "1.0.0"
__all__ = [
    # Models
    "Circuit",
    "VisualElement",
    "Wire",
    "Position",
    # Managers
    "CircuitManager",
    "ElementManager",
    "WireManager",
    # Parser
    "CircuitXMLParser",
    # Exceptions
    "DigitalHDKError",
    "PositionOccupiedError",
    "InvalidElementError",
    "InvalidWireError",
    "WireAlreadyExists",
    "ParseError",
    "ValidationError",
]

