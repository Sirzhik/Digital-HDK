


class DigitalHDKError(Exception):
    """Basic HDK exception"""
    pass


class PositionOccupiedError(DigitalHDKError):
    """Position is already in use by another element."""
    pass


class InvalidElementError(DigitalHDKError):
    """Invalid element name."""
    pass


class InvalidWireError(DigitalHDKError):
    """Invalid wire connection (points overlap, etc.)."""
    pass


class WireAlreadyExists(DigitalHDKError):
    """Wire connection between these points already exists."""
    pass


class ParseError(DigitalHDKError):
    """Error occurred while parsing XML."""
    pass


class ValidationError(DigitalHDKError):
    """Error occurred while validating schema structure."""
    pass
