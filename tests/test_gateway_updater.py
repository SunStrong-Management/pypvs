"""Tests for the gateway updater with and without flash wear (PVS5)."""

from __future__ import annotations

import asyncio

import pytest

from pypvs.exceptions import (
    PVSAuthenticationError,
    PVSCommunicationError,
    PVSDataFormatError,
)
from pypvs.models.common import CommonProperties
from pypvs.models.pvs import PVSData
from pypvs.updaters.gateway import PVSGatewayUpdater

FLASHWEAR = "/sys/pvs/flashwear_type_b"
SYS_INFO = {
    "/sys/info/sys_type": "PV-only",
    "/sys/info/model": "PVS5",
    "/sys/info/hwrev": "5.1",
    "/sys/info/sw_rev": "5412",
    "/sys/info/uptime": "1000.0",
    "/sys/info/lmac": "00:00:00:00:00:00",
    "/sys/info/ram_usage": "40",
    "/sys/info/flash_usage": "50",
    "/sys/info/cpu_usage": "10",
}


class FakePVS:
    """Answer varserver requests, failing for the flash wear var if set."""

    def __init__(self, flashwear: str | Exception) -> None:
        self.flashwear = flashwear
        self.requested: list[str] = []

    async def request_var(self, name: str) -> str:
        self.requested.append(name)
        if name != FLASHWEAR:
            return SYS_INFO[name]
        if isinstance(self.flashwear, Exception):
            raise self.flashwear
        return self.flashwear


def setup_updater(pvs: FakePVS) -> PVSGatewayUpdater:
    updater = PVSGatewayUpdater(pvs.request_var, None, CommonProperties())
    asyncio.run(updater.probe(None))
    return updater


@pytest.mark.parametrize(
    "error",
    [
        pytest.param(PVSDataFormatError("no values"), id="no_values"),
        pytest.param(PVSCommunicationError("HTTP 400"), id="http_400"),
        pytest.param(PVSAuthenticationError("HTTP 500"), id="http_500"),
    ],
)
def test_pvs_without_flashwear(error: Exception) -> None:
    """The gateway is updated and flash wear is only requested in the probe."""
    pvs = FakePVS(error)
    updater = setup_updater(pvs)

    for _ in range(2):
        data = PVSData()
        asyncio.run(updater.update(data))
        assert data.gateway.software_version == "5412"
        assert data.gateway.flashwear_type_b_percent is None
    assert pvs.requested.count(FLASHWEAR) == 1


def test_pvs_with_flashwear() -> None:
    """Flash wear is read on every update when the probe found it."""
    pvs = FakePVS("0x03")
    updater = setup_updater(pvs)

    data = PVSData()
    asyncio.run(updater.update(data))
    assert data.gateway.flashwear_type_b_percent == 30
    assert pvs.requested.count(FLASHWEAR) == 2


def test_flashwear_failing_after_probe() -> None:
    """A failing flash wear read does not fail the gateway update."""
    pvs = FakePVS("0x03")
    updater = setup_updater(pvs)
    pvs.flashwear = PVSCommunicationError("HTTP 500")

    data = PVSData()
    asyncio.run(updater.update(data))
    assert data.gateway.software_version == "5412"
    assert data.gateway.flashwear_type_b_percent is None
