"""Python wrapper for SunStrong Management PVS API."""

from .pvs import PVS
from .exceptions import (
    PVSError,
    PVSFirmwareCheckError,
    PVSAuthenticationError,
    PVSCommunicationError,
    PVSDataFormatError,
)
from .models.inverter import PVSInverter

__all__ = (
    "register_updater",
    "PVS",
    "PVSError",
    "PVSCommunicationError",
    "PVSFirmwareCheckError",
    "PVSAuthenticationError",
    "PVSInverter",
)

try:
    from ._version import __version__
except Exception:  # fallback in weird environments
    __version__ = "0+unknown"
