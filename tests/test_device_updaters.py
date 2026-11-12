"""Tests for device updaters with devices that report no serial number."""

from __future__ import annotations

import asyncio

import pytest

from pypvs.const import (
    VARS_MATCH_ESS,
    VARS_MATCH_INVERTERS,
    VARS_MATCH_METERS,
    VARS_MATCH_TRANSFER_SWITCH,
)
from pypvs.models.common import CommonProperties
from pypvs.models.pvs import PVSData
from pypvs.updaters.ess import PVSESSUpdater
from pypvs.updaters.meter import PVSProductionMetersUpdater
from pypvs.updaters.production_inverters import PVSProductionInvertersUpdater
from pypvs.updaters.transfer_switch import PVSTransferSwitchUpdater


@pytest.mark.parametrize(
    ("updater_class", "match", "attribute"),
    [
        pytest.param(
            PVSProductionMetersUpdater, VARS_MATCH_METERS, "meters", id="meters"
        ),
        pytest.param(
            PVSProductionInvertersUpdater,
            VARS_MATCH_INVERTERS,
            "inverters",
            id="inverters",
        ),
        pytest.param(PVSESSUpdater, VARS_MATCH_ESS, "ess", id="ess"),
        pytest.param(
            PVSTransferSwitchUpdater,
            VARS_MATCH_TRANSFER_SWITCH,
            "transfer_switches",
            id="transfer_switches",
        ),
    ],
)
def test_device_without_serial_number(
    updater_class: type, match: str, attribute: str
) -> None:
    """A device without a serial number is skipped, the others are updated."""

    async def request_vars(name: str) -> dict[str, str]:
        assert name == match
        return {
            f"{match}0/sn": "SN0",
            f"{match}0/prodMdlNm": "MODEL",
            f"{match}1/prodMdlNm": "MODEL",
        }

    updater = updater_class(None, request_vars, CommonProperties())
    data = PVSData()
    asyncio.run(updater.update(data))
    assert list(getattr(data, attribute)) == ["SN0"]
