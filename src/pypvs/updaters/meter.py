import logging
from typing import Any

from ..const import VARS_MATCH_METERS, SupportedFeatures
from ..exceptions import ENDPOINT_PROBE_EXCEPTIONS
from ..models.meter import PVSMeter
from ..models.pvs import PVSData
from .base import PVSUpdater

_LOGGER = logging.getLogger(__name__)


class PVSProductionMetersUpdater(PVSUpdater):
    """Class to handle updates for meter data."""

    async def probe(
        self, discovered_features: SupportedFeatures
    ) -> SupportedFeatures | None:
        """Probe the PVS for this updater and return SupportedFeatures."""
        try:
            await self._request_vars(VARS_MATCH_METERS)
        except ENDPOINT_PROBE_EXCEPTIONS as e:
            _LOGGER.debug(
                "No meters found on varserver filter %s: %s", VARS_MATCH_METERS, e
            )
            return None
        self._supported_features |= SupportedFeatures.METERING
        return self._supported_features

    async def update(self, pvs_data: PVSData) -> None:
        """Update the PVS for this updater."""
        try:
            meters_dict: list[dict[str, Any]] = await self._request_vars(
                VARS_MATCH_METERS
            )
        except Exception as e:
            _LOGGER.error("Failed to request meter vars: %s", e)
            return

        try:
            # construct a list of meters from the provided dictionary,
            #  drop all parent path
            meters_grouped = {}
            for key, val in meters_dict.items():
                # Extract the meter index from the name, e.g., '0'
                # from '/sys/devices/meter/0/freqHz'
                parts = key.split("/")
                if len(parts) >= 5:
                    idx = int(parts[4])
                    param = parts[5]
                    if idx not in meters_grouped:
                        meters_grouped[idx] = {param: val}
                    else:
                        meters_grouped[idx][param] = val

            # Convert to a list sorted by index
            meters_data = [
                meters_grouped[idx] for idx in sorted(meters_grouped.keys(), key=int)
            ]
        except Exception as e:
            _LOGGER.error("Failed to process meter data: %s", e)
            return

        pvs_data.raw[VARS_MATCH_METERS] = meters_data
        pvs_data.meters = {
            meter["sn"]: PVSMeter.from_varserver(meter) for meter in meters_data
        }
