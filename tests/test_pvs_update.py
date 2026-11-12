"""Tests for a full setup and update against the variables of a real PVS.

The fixtures are the same as in the pvs-hass tests: variables captured from a
PVS6, anonymized, and a PVS5 derived from them.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from pypvs.exceptions import PVSCommunicationError
from pypvs.models.pvs import PVSData
from pypvs.pvs import PVS

FIXTURES = Path(__file__).parent / "fixtures"


def pvs_with_variables(variables: dict[str, str]) -> PVS:
    pvs = PVS(session=None, host="127.0.0.1")

    async def get_varserver(path, params=None):
        if "name" in params:
            if params["name"] not in variables:
                # A PVS answers HTTP 400 for a variable it does not have
                raise PVSCommunicationError("POST request failed: 400")
            names = [params["name"]]
        else:
            names = [name for name in variables if name.startswith(params["match"])]
        return {
            "count": len(names),
            "values": [{"name": name, "value": variables[name]} for name in names],
        }

    pvs.getVarserver = get_varserver
    return pvs


async def setup_and_update(pvs: PVS) -> PVSData:
    await pvs.setup()
    return await pvs.update()


@pytest.mark.parametrize(
    (
        "fixture",
        "serial_number",
        "model",
        "flashwear",
        "inverters",
        "meters",
    ),
    [
        pytest.param(
            "pvs6",
            "ZT000000000000T0001",
            "PVS6",
            30,
            {"E00000000000001", "E00000000000002"},
            {"PVS6M00000001p", "PVS6M00000001c"},
            id="pvs6",
        ),
        pytest.param(
            "pvs5",
            "ZA000000000000T0002",
            "PVS5",
            None,
            {"E00000000000003", "E00000000000004"},
            {"PVS5M00000002p", "PVS5M00000002c"},
            id="pvs5",
        ),
    ],
)
def test_update(
    fixture: str,
    serial_number: str,
    model: str,
    flashwear: int | None,
    inverters: set[str],
    meters: set[str],
) -> None:
    variables = json.loads((FIXTURES / f"{fixture}.json").read_text())
    pvs = pvs_with_variables(variables)

    data = asyncio.run(setup_and_update(pvs))

    assert pvs.serial_number == serial_number
    assert data.gateway.hardware_version.startswith(model)
    assert data.gateway.flashwear_type_b_percent == flashwear
    assert set(data.inverters) == inverters
    assert set(data.meters) == meters
    assert data.inverters[min(inverters)].lte_kwh == pytest.approx(5279.367676)
    assert data.meters[min(meters)].net_lte_kwh == pytest.approx(2775.040039)
    assert data.ess == {}
    assert data.transfer_switches == {}
