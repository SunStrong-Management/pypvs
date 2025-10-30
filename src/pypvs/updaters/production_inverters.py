import logging
from typing import Any

from ..const import VARS_MATCH_INVERTERS, SupportedFeatures
from ..exceptions import ENDPOINT_PROBE_EXCEPTIONS
from ..models.inverter import PVSInverter
from ..models.pvs import PVSData
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
        try:
            inverters_dict: list[dict[str, Any]] = await self._request_vars(
                VARS_MATCH_INVERTERS
            )
        except Exception as e:
            _LOGGER.error("Failed to request inverter vars: %s", e)
            return

        try:
            # construct a list of inverters from the provided dictionary, drop all parent path
            inverters_grouped = {}
            for key, val in inverters_dict.items():
                # Extract the inverter index from the name, e.g., '0' from '/sys/devices/inverter/0/freqHz'
                parts = key.split("/")
                if len(parts) >= 5:
                    idx = int(parts[4])
                    param = parts[5]
                    if idx not in inverters_grouped:
                        inverters_grouped[idx] = {param: val}
                    else:
                        inverters_grouped[idx][param] = val

            # Convert to a list sorted by index
            inverters_data = [
                inverters_grouped[idx]
                for idx in sorted(inverters_grouped.keys(), key=int)
            ]
        except Exception as e:
            _LOGGER.error("Failed to process inverter data: %s", e)
            return

        pvs_data.raw[VARS_MATCH_INVERTERS] = inverters_data
        pvs_data.inverters = {
            inverter["sn"]: PVSInverter.from_varserver(inverter)
            for inverter in inverters_data
        }
