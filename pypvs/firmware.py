"""PVS Firmware detection"""

from .exceptions import PVSFirmwareCheckError
from typing import Awaitable, Callable, Any

class PVSFirmware:
    """Class for querying and determining the PVS firmware version."""
    def __init__(
        self,
        request_var: Callable[[str], Awaitable[Any]],
    ) -> None:
        """Initialize the PVS firmware version."""
        self._request_var = request_var
        self._serial_number: str | None = None
        self._ssid: str | None = None
        self._lmac: str | None = None

    async def setup(self) -> None:
        """Obtain the system informaton needed for PVS authentication."""
        try:
            self._serial_number = await self._request_var("/sys/info/serialnum")
            self._ssid = await self._request_var("/sys/info/ssid")
            self._lmac = await self._request_var("/sys/info/lmac")
        except KeyError as e:
            raise PVSFirmwareCheckError(f"Cannot extract system information from response {e}")

    @property
    def serial(self) -> str | None:
        return self._serial_number
    
    @property
    def ssid(self) -> str | None:
        return self._ssid

    @property
    def lmac(self) -> str | None:
        return self._lmac
