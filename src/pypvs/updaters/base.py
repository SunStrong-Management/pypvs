from abc import abstractmethod
from typing import Any, Awaitable, Callable

from ..const import SupportedFeatures
from ..models.common import CommonProperties
from ..models.pvs import PVSData


class PVSUpdater:
    """Base class for PVS updaters."""

    def __init__(
        self,
        request_var: Callable[[str], Awaitable[Any]],
        request_vars: Callable[[str], Awaitable[dict[str, Any]]],
        common_properties: CommonProperties,
    ) -> None:
        """Initialize the PVS updater."""
        self._request_var = request_var
        self._request_vars = request_vars
        self._supported_features = SupportedFeatures(0)
        self._common_properties = common_properties

    @abstractmethod
    async def probe(
        self, discovered_features: SupportedFeatures
    ) -> SupportedFeatures | None:
        """Probe the PVS for this updater and return SupportedFeatures."""

    @abstractmethod
    async def update(self, pvs_data: PVSData) -> None:
        """Update the PVS for this updater."""
