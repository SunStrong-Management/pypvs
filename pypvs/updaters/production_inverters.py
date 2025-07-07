import logging
from typing import Any

from ..const import SupportedFeatures, VARS_MATCH_INVERTERS
from ..exceptions import ENDPOINT_PROBE_EXCEPTIONS
from ..models.pvs import PVSData
from ..models.inverter import PVSInverter
from .base import PVSUpdater

_LOGGER = logging.getLogger(__name__)


class PVSProductionInvertersUpdater(PVSUpdater):
    """Class to handle updates for inverter production data."""

    async def probe(
        self, discovered_features: SupportedFeatures
    ) -> SupportedFeatures | None:
        """Probe the PVS for this updater and return SupportedFeatures."""
        try:
            await self._request_vars(VARS_MATCH_INVERTERS)
        except ENDPOINT_PROBE_EXCEPTIONS as e:
            _LOGGER.debug(
                "No inverters found on varserver filter %s: %s", VARS_MATCH_INVERTERS, e
            )
            return None
        self._supported_features |= SupportedFeatures.INVERTERS
        return self._supported_features

    async def update(self, pvs_data: PVSData) -> None:
        """Update the PVS for this updater."""
        inverters_dict: list[dict[str, Any]] = await self._request_vars(VARS_MATCH_INVERTERS)

        # construct a list from the provided dictionary, we don't need the paths
        inverters_data = [inverter for inverter in inverters_dict.values()]

        pvs_data.raw[VARS_MATCH_INVERTERS] = inverters_data
        pvs_data.inverters = {
            inverter["sn"]: PVSInverter.from_varserver(inverter)
            for inverter in inverters_data
        }
