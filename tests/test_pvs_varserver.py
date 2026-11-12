"""Tests for reading varserver vars from unexpected responses."""

from __future__ import annotations

import asyncio

import pytest

from pypvs.exceptions import PVSDataFormatError
from pypvs.pvs import PVS


def pvs_returning(response: object) -> PVS:
    pvs = PVS(session=None, host="127.0.0.1")

    async def get_varserver(path, params=None):
        return response

    pvs.getVarserver = get_varserver
    return pvs


@pytest.mark.parametrize(
    "response",
    [
        pytest.param({"count": 0, "values": []}, id="no_values"),
        pytest.param({"count": 0, "values": None}, id="values_null"),
        pytest.param({"values": ["0x01"]}, id="value_not_object"),
        pytest.param({}, id="no_values_key"),
    ],
)
def test_get_var_unexpected_response(response: object) -> None:
    with pytest.raises(PVSDataFormatError):
        asyncio.run(pvs_returning(response).getVarserverVar("/sys/info/uptime"))


@pytest.mark.parametrize(
    "response",
    [
        pytest.param({"count": 0, "values": None}, id="values_null"),
        pytest.param({"values": ["0x01"]}, id="value_not_object"),
        pytest.param({}, id="no_values_key"),
    ],
)
def test_get_vars_unexpected_response(response: object) -> None:
    with pytest.raises(PVSDataFormatError):
        asyncio.run(pvs_returning(response).getVarserverVars("/sys/devices/meter/"))
