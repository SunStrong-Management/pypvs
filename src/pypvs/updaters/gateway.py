import logging
from typing import Any

from ..const import SupportedFeatures, VARS_MATCH_INFO
from ..models.pvs import PVSData
from ..models.gateway import PVSGateway
from .base import PVSUpdater

_LOGGER = logging.getLogger(__name__)


class PVSGatewayUpdater(PVSUpdater):
    """Class to handle updates for the PVS gateway."""

    async def probe(
        self, discovered_features: SupportedFeatures
    ) -> SupportedFeatures | None:
        """Probe the PVS for this updater and return SupportedFeatures."""

        # This updater is always available
        _LOGGER.debug("Probing PVS for gateway data. It is aways available.")
        self._supported_features |= SupportedFeatures.GATEWAY
        return self._supported_features

    async def update(self, pvs_data: PVSData) -> None:
        """Update the PVS for this updater."""
        sys_info: list[dict[str, Any]] = {
            "/sys/info/sys_type": None,
            "/sys/info/model": None,
            "/sys/info/hwrev": None,
            "/sys/info/sw_rev": None,
            "/sys/info/uptime": None,
            "/sys/info/lmac": None,
            "/sys/info/ram_usage": None,
            "/sys/info/flash_usage": None,
            "/sys/info/cpu_usage": None,
        }

        # undate individual vars and not by match as the match takes a long time
        for var_name, var_value in sys_info.items():
            if var_value is None:
                sys_info[var_name] = await self._request_var(var_name)

        pvs_data.raw[VARS_MATCH_INFO] = sys_info
        pvs_data.gateway = PVSGateway.from_varserver(sys_info)
