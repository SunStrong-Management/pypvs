import logging
from typing import Any

from ..const import VARS_MATCH_TRANSFER_SWITCH, SupportedFeatures
from ..exceptions import ENDPOINT_PROBE_EXCEPTIONS
from ..models.pvs import PVSData
from ..models.transfer_switch import PVSTransferSwitch
from .base import PVSUpdater

_LOGGER = logging.getLogger(__name__)


class PVSTransferSwitchUpdater(PVSUpdater):
    """Class to handle updates for transfer switch data."""

    async def probe(
        self, discovered_features: SupportedFeatures
    ) -> SupportedFeatures | None:
        """Probe the PVS for this updater and return SupportedFeatures."""
        try:
            await self._request_vars(VARS_MATCH_TRANSFER_SWITCH)
        except ENDPOINT_PROBE_EXCEPTIONS as e:
            _LOGGER.debug(
                "No transfer switches found on varserver filter %s: %s",
                VARS_MATCH_TRANSFER_SWITCH,
                e,
            )
            return None
        self._supported_features |= SupportedFeatures.TRANSFER_SWITCH
        return self._supported_features

    async def update(self, pvs_data: PVSData) -> None:
        """Update the PVS for this updater."""
        try:
            transfer_switches_dict: list[dict[str, Any]] = await self._request_vars(
                VARS_MATCH_TRANSFER_SWITCH
            )
        except Exception as e:
            _LOGGER.error("Failed to request transfer switch vars: %s", e)
            return

        try:
            # construct a list of transfer switches from the provided dictionary,
            # drop all parent path
            transfer_switches_grouped = {}
            for key, val in transfer_switches_dict.items():
                # Extract the transfer switch index from the name, e.g., '0'
                # from '/sys/devices/transfer_switch/0/state'
                parts = key.split("/")
                if len(parts) >= 5:
                    idx = int(parts[4])
                    param = parts[5]
                    if idx not in transfer_switches_grouped:
                        transfer_switches_grouped[idx] = {param: val}
                    else:
                        transfer_switches_grouped[idx][param] = val

            # Convert to a list sorted by index
            transfer_switches_data = [
                transfer_switches_grouped[idx]
                for idx in sorted(transfer_switches_grouped.keys(), key=int)
            ]
        except Exception as e:
            _LOGGER.error("Failed to process transfer switch data: %s", e)
            return

        pvs_data.raw[VARS_MATCH_TRANSFER_SWITCH] = transfer_switches_data
        pvs_data.transfer_switches = {
            switch["sn"]: PVSTransferSwitch.from_varserver(switch)
            for switch in transfer_switches_data
        }
