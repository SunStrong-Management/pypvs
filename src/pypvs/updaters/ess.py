import logging
from typing import Any

from ..const import VARS_MATCH_ESS, SupportedFeatures
from ..exceptions import ENDPOINT_PROBE_EXCEPTIONS
from ..models.ess import PVSESS
from ..models.pvs import PVSData
from .base import PVSUpdater

_LOGGER = logging.getLogger(__name__)


class PVSESSUpdater(PVSUpdater):
    """Class to handle updates for ESS data."""

    async def probe(
        self, discovered_features: SupportedFeatures
    ) -> SupportedFeatures | None:
        """Probe the PVS for this updater and return SupportedFeatures."""
        try:
            await self._request_vars(VARS_MATCH_ESS)
        except ENDPOINT_PROBE_EXCEPTIONS as e:
            _LOGGER.debug("No ESS found on varserver filter %s: %s", VARS_MATCH_ESS, e)
            return None
        self._supported_features |= SupportedFeatures.ESS
        return self._supported_features

    async def update(self, pvs_data: PVSData) -> None:
        """Update the PVS for this updater."""
        try:
            ess_dict: list[dict[str, Any]] = await self._request_vars(VARS_MATCH_ESS)
        except Exception as e:
            _LOGGER.error("Failed to request ESS vars: %s", e)
            return

        try:
            # construct a list of ESS from the provided dictionary, drop all parent path
            ess_grouped = {}
            for key, val in ess_dict.items():
                # Extract the ESS index from the name, e.g., '0'
                # from '/sys/devices/ess/0/opMode'
                parts = key.split("/")
                if len(parts) >= 5:
                    idx = int(parts[4])
                    param = parts[5]
                    if idx not in ess_grouped:
                        ess_grouped[idx] = {param: val}
                    else:
                        ess_grouped[idx][param] = val

            # Convert to a list sorted by index
            ess_data = [ess_grouped[idx] for idx in sorted(ess_grouped.keys(), key=int)]
        except Exception as e:
            _LOGGER.error("Failed to process ESS data: %s", e)
            return

        pvs_data.raw[VARS_MATCH_ESS] = ess_data
        pvs_data.ess = {ess["sn"]: PVSESS.from_varserver(ess) for ess in ess_data}
