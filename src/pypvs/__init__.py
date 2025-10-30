"""Python wrapper for SunStrong Management PVS API."""

# isort: off
from .exceptions import (
    PVSAuthenticationError,
    PVSCommunicationError,
    PVSDataFormatError,
    PVSError,
    PVSFirmwareCheckError,
)

# isort: on
from .models.inverter import PVSInverter
from .pvs import PVS

__all__ = (
    "register_updater",
    "PVS",
    "PVSError",
    "PVSCommunicationError",
    "PVSDataFormatError",
    "PVSFirmwareCheckError",
    "PVSAuthenticationError",
    "PVSInverter",
)

try:
    from ._version import __version__
except Exception:  # fallback in weird environments
    __version__ = "0+unknown"
