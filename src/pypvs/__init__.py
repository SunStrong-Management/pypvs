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
from .models.livedata import PVSLiveData
from .pvs import PVS
from .pvs_websocket import ConnectionState, PVSWebSocket

__all__ = (
    "register_updater",
    "PVS",
    "PVSError",
    "PVSCommunicationError",
    "PVSDataFormatError",
    "PVSFirmwareCheckError",
    "PVSAuthenticationError",
    "PVSInverter",
    "PVSLiveData",
    "PVSWebSocket",
    "ConnectionState",
)

try:
    from ._version import __version__
except Exception:  # fallback in weird environments
    __version__ = "0+unknown"
