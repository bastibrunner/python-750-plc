"""Wago 750 Error Codes."""

from .const import ERROR_CODES

class WagoException(Exception):
    """Base exception for Wago PLC errors."""

    def __init__(self, message: str, error_code: int | None = None) -> None:
        """Initialize the exception.

        Args:
            message: The error message
            error_code: Optional error code from error_codes dict

        """
        if error_code is not None and error_code in ERROR_CODES:
            message = f"{message}: {ERROR_CODES[error_code]}"
        super().__init__(message)
