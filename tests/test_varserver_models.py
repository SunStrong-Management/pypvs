"""Tests for parsing varserver payloads into models.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

import pytest

from pypvs.exceptions import PVSFirmwareCheckError
from pypvs.firmware import PVSFirmware
from pypvs.models.ess import PVSESS
from pypvs.models.gateway import PVSGateway
from pypvs.models.inverter import PVSInverter
from pypvs.models.livedata import PVSLiveData
from pypvs.models.meter import PVSMeter
from pypvs.models.transfer_switch import PVSTransferSwitch

# Canonical sample instant for msmtEps and /sys/livedata/time in this module.
SAMPLE_TS_UTC = datetime.strptime(
    "2026-04-10T11:30:00Z", "%Y-%m-%dT%H:%M:%SZ"
).replace(tzinfo=timezone.utc)
SAMPLE_UNIX = int(SAMPLE_TS_UTC.timestamp())

# --- Inverter
INVERTER_SAMPLE_SN = "E00987654321001"
INVERTER_SAMPLE = {
    "freqHz": 59.98,
    "i3phsumA": 1.21,
    "iMppt1A": 5.4,
    "ltea3phsumKwh": 2843.847168,
    "msmtEps": "2026-04-10T11:30:00Z",
    "p3phsumKw": 0.29659,
    "pMppt1Kw": 0.25992,
    "prodMdlNm": "AC_Module_Type_E",
    "sn": INVERTER_SAMPLE_SN,
    "tHtsnkDegc": 29,
    "vMppt1V": 48.09,
    "vln3phavgV": 244.070007,
}

# --- Gateway
GATEWAY_SYS_INFO_ANON = {
    "/sys/info/model": "PVS6 ",
    "/sys/info/hwrev": "6.02 ",
    "/sys/info/sys_type": "Storage ",
    "/sys/info/sw_rev": "2025.01.01.90001",
    "/sys/info/uptime": 14042.9,
    "/sys/info/lmac": "02:aa:bb:cc:dd:01",
    "/sys/info/ram_usage": 7,
    "/sys/info/flash_usage": 73,
    "/sys/info/cpu_usage": 6,
}

# --- Meters
METER_PRODUCTION_ANON = {
    "msmtEps": "2026-04-10T11:30:00Z",
    "sn": "PVS6M90000001p",
    "prodMdlNm": "PVS6M0400p",
    "ctSclFctr": 100,
    "freqHz": 59.988712,
    "i1A": 0.0,
    "i2A": 0.0,
    "negLtea3phsumKwh": 0.0,
    "netLtea3phsumKwh": 11991.549805,
    "p1Kw": 0.0,
    "p2Kw": 0.0,
    "p3phsumKw": 2.972999,
    "posLtea3phsumKwh": 0.0,
    "q3phsumKvar": 0.184966,
    "s3phsumKva": 2.982468,
    "totPfRto": 0.996842,
    "v12V": 243.58197,
    "v1nV": 0.0,
    "v2nV": 0.0,
}

METER_NET_ANON = {
    "msmtEps": "2026-04-10T11:30:00Z",
    "sn": "PVS6M90000002c",
    "prodMdlNm": "PVS6M0400c",
    "ctSclFctr": 100,
    "freqHz": 59.988712,
    "i1A": 5.867875,
    "i2A": 6.082969,
    "negLtea3phsumKwh": 5842.859863,
    "netLtea3phsumKwh": -5842.830078,
    "p1Kw": -0.711292,
    "p2Kw": -0.738008,
    "p3phsumKw": -1.449301,
    "posLtea3phsumKwh": 0.01,
    "q3phsumKvar": -0.101444,
    "s3phsumKva": 1.455515,
    "totPfRto": -0.995831,
    "v12V": 243.58197,
    "v1nV": 121.751556,
    "v2nV": 121.830658,
}

# --- Transfer switch
TRANSFER_SWITCH_ANON = {
    "msmtEps": "2026-04-10T11:30:00Z",
    "sn": "MIDC-TEST-UNIT-01",
    "prodMdlNm": "SunPower MIDC",
    "midStEnum": "MID_STATE_CLOSED",
    "pvd1StEnum": "PVD_STATE_CLOSED",
    "tDegc": 28.0,
    "v1nGridV": 122.41333,
    "v1nV": 122.519333,
    "v2nGridV": 122.514664,
    "v2nV": 122.414665,
    "vSpplyV": 11.237206,
}

# --- ESS
ESS_ANON_SN = "ESS-TEST-UNIT-00001"
ESS_ANON = {
    "msmtEps": "2026-04-10T11:30:00Z",
    "sn": ESS_ANON_SN,
    "prodMdlNm": "SPWR-Equinox-model",
    "chrgLimitPmaxKw": 10.762,
    "customerSocVal": 0.59,
    "dischrgLimPmaxKw": 10.004,
    "maxTBattCellDegc": 30.059999,
    "maxVBattCellV": 3.28275,
    "minTBattCellDegc": 2.33,
    "minVBattCellV": 3.27965,
    "negLtea3phsumKwh": 7492.96582,
    "opMode": "ENERGY_ARBITRAGE",
    "p3phsumKw": 0.326787,
    "posLtea3phsumKwh": 5672.499023,
    "socVal": 0.65,
    "sohVal": 1,
    "tInvtrDegc": 36.619999,
    "v1nV": 122.489265,
    "v2nV": 122.489265,
    "vBattV": 52.445,
}

# --- Live data
LIVEDATA_ANON = {
    "/sys/livedata/time": SAMPLE_UNIX,
    "/sys/livedata/pv_p": 2.971486,
    "/sys/livedata/pv_en": 11992.030273,
    "/sys/livedata/net_p": -1.44736,
    "/sys/livedata/net_en": -5843.060059,
    "/sys/livedata/site_load_p": 1.524126,
    "/sys/livedata/site_load_en": 6148.970215,
    "/sys/livedata/ess_en": "nan",
    "/sys/livedata/ess_p": "nan",
    "/sys/livedata/soc": "nan",
    "/sys/livedata/backupTimeRemaining": 0,
    "/sys/livedata/midstate": 2,
}

# Live data with ESS fields
LIVEDATA_WITH_ESS_ANON = {
    "/sys/livedata/time": SAMPLE_UNIX,
    "/sys/livedata/pv_p": 0.014,
    "/sys/livedata/pv_en": 24890.25,
    "/sys/livedata/net_p": 0.015,
    "/sys/livedata/net_en": -8750.0,
    "/sys/livedata/site_load_p": 0.382,
    "/sys/livedata/site_load_en": 14500.0,
    "/sys/livedata/ess_en": -1800.5,
    "/sys/livedata/ess_p": 0.35,
    "/sys/livedata/soc": 0.575,
    "/sys/livedata/backupTimeRemaining": 1100,
    "/sys/livedata/midstate": 2,
}


def test_inverter_from_varserver_omitted_float_fields():
    """Missing numeric keys (e.g. tHtsnkDegc) must not raise TypeError."""
    inv = PVSInverter.from_varserver(
        {
            "sn": "ABC",
            "prodMdlNm": "INV1",
            "msmtEps": "2026-04-10T11:30:00Z",
        }
    )
    assert inv.serial_number == "ABC"
    assert inv.model == "INV1"
    assert inv.last_report_date == SAMPLE_UNIX
    assert inv.last_report_temperature_c == 0.0
    assert inv.last_report_kw == 0.0
    assert inv.last_report_voltage_v == 0.0
    assert inv.last_report_current_a == 0.0
    assert inv.last_report_frequency_hz == 0.0
    assert inv.lte_kwh == 0.0
    assert inv.last_mppt_voltage_v == 0.0
    assert inv.last_mppt_current_a == 0.0
    assert inv.last_mppt_power_kw == 0.0


def test_inverter_from_varserver_sample_payload():
    """Inverter dict shaped like packed /sys/devices/inverter/{i}/* telemetry."""
    inv = PVSInverter.from_varserver(INVERTER_SAMPLE)
    assert inv.serial_number == INVERTER_SAMPLE_SN
    assert inv.model == "AC_Module_Type_E"
    assert inv.last_report_date == SAMPLE_UNIX
    assert inv.last_report_kw == 0.29659
    assert inv.last_report_voltage_v == 244.070007
    assert inv.last_report_current_a == 1.21
    assert inv.last_report_frequency_hz == 59.98
    assert inv.last_report_temperature_c == 29.0
    assert inv.lte_kwh == 2843.847168
    assert inv.last_mppt_voltage_v == 48.09
    assert inv.last_mppt_current_a == 5.4
    assert inv.last_mppt_power_kw == 0.25992


def test_gateway_from_varserver_omitted_numeric_fields():
    """Missing uptime / usage keys must not raise TypeError."""
    gw = PVSGateway.from_varserver(
        {
            "/sys/info/model": "M ",
            "/sys/info/hwrev": "1 ",
            "/sys/info/sys_type": "T ",
        }
    )
    assert gw.uptime_s == 0.0
    assert gw.ram_usage_percent == 0
    assert gw.flash_usage_percent == 0
    assert gw.cpu_usage_percent == 0
    assert gw.flashwear_type_b_percent is None


def test_gateway_from_varserver_full_sys_info_shape():
    """Typical /sys/info blob from a PVS6"""
    gw = PVSGateway.from_varserver(GATEWAY_SYS_INFO_ANON)
    assert gw.model == "Storage"
    assert gw.pvs_type == "PVS6"
    assert gw.hardware_version == "PVS6 6.02"
    assert gw.software_version == "2025.01.01.90001"
    assert gw.uptime_s == 14042.9
    assert gw.mac == "02:aa:bb:cc:dd:01"
    assert gw.ram_usage_percent == 7
    assert gw.flash_usage_percent == 73
    assert gw.cpu_usage_percent == 6
    assert gw.flashwear_type_b_percent is None


def test_gateway_flashwear_normal_value():
    """PVS6 with flashwear 0x05 → 50%."""
    data = {**GATEWAY_SYS_INFO_ANON, "/sys/pvs/flashwear_type_b": "0x05"}
    gw = PVSGateway.from_varserver(data)
    assert gw.flashwear_type_b_percent == 50


def test_gateway_flashwear_capped_at_100():
    """Raw values above 0x0A are capped at 100%."""
    data = {**GATEWAY_SYS_INFO_ANON, "/sys/pvs/flashwear_type_b": "0x0B"}
    gw = PVSGateway.from_varserver(data)
    assert gw.flashwear_type_b_percent == 100


def test_gateway_flashwear_invalid_hex():
    """Invalid hex string returns None."""
    data = {**GATEWAY_SYS_INFO_ANON, "/sys/pvs/flashwear_type_b": "garbage"}
    gw = PVSGateway.from_varserver(data)
    assert gw.flashwear_type_b_percent is None


def test_meter_from_varserver_production_and_net_shapes():
    """Gross-production and net-consumption meters without optional AC sum fields."""
    prod = PVSMeter.from_varserver(METER_PRODUCTION_ANON)
    assert prod.serial_number == "PVS6M90000001p"
    assert prod.model == "PVS6M0400p"
    assert prod.last_report_date == SAMPLE_UNIX
    assert prod.power_3ph_kw == 2.972999
    assert prod.freq_hz == 59.988712
    assert prod.net_lte_kwh == 11991.549805
    assert prod.v12_v == 243.58197
    assert prod.voltage_3ph_v == 0.0
    assert prod.current_3ph_a == 0.0
    assert prod.lte_3ph_kwh == 0.0

    net = PVSMeter.from_varserver(METER_NET_ANON)
    assert net.last_report_date == SAMPLE_UNIX
    assert net.serial_number == "PVS6M90000002c"
    assert net.power_3ph_kw == -1.449301
    assert net.v1n_v == 121.751556
    assert net.v2n_v == 121.830658
    assert net.neg_lte_kwh == 5842.859863
    assert net.tot_pf_ratio == -0.995831


def test_transfer_switch_from_varserver_sample_shape():
    """MIDC row matching typical /sys/devices/transfer_switch/0/* layout."""
    ts = PVSTransferSwitch.from_varserver(TRANSFER_SWITCH_ANON)
    assert ts.last_report_date == SAMPLE_UNIX
    assert ts.serial_number == "MIDC-TEST-UNIT-01"
    assert ts.model == "SunPower MIDC"
    assert ts.mid_state == "MID_STATE_CLOSED"
    assert ts.pvd1_state == "PVD_STATE_CLOSED"
    assert ts.temperature_c == 28.0
    assert ts.v_supply_v == 11.237206


def test_livedata_from_varserver_numeric_and_nan_strings():
    """Live data paths; string 'nan' for absent ESS becomes None."""
    ld = PVSLiveData.from_varserver(LIVEDATA_ANON)
    assert ld.time == SAMPLE_TS_UTC
    assert ld.pv_p == 2.971486
    assert ld.pv_en == 11992.030273
    assert ld.net_p == -1.44736
    assert ld.net_en == -5843.060059
    assert ld.site_load_p == 1.524126
    assert ld.site_load_en == 6148.970215
    assert ld.ess_en is None
    assert ld.ess_p is None
    assert ld.soc is None
    assert ld.backup_time_remaining == 0.0
    assert ld.midstate == 2


def test_livedata_from_varserver_with_ess_fields():
    """ESS energy/power, SoC, and backup time parse when present (not nan)."""
    ld = PVSLiveData.from_varserver(LIVEDATA_WITH_ESS_ANON)
    assert ld.time == SAMPLE_TS_UTC
    assert ld.pv_p == 0.014
    assert ld.pv_en == 24890.25
    assert ld.net_p == 0.015
    assert ld.net_en == -8750.0
    assert ld.site_load_p == 0.382
    assert ld.site_load_en == 14500.0
    assert ld.ess_en == -1800.5
    assert ld.ess_p == 0.35
    assert ld.soc == 0.575
    assert ld.backup_time_remaining == 1100.0
    assert ld.midstate == 2


def test_ess_from_varserver_sample_payload():
    """ESS row shaped like /sys/devices/ess/* packed JSON."""
    ess = PVSESS.from_varserver(ESS_ANON)
    assert ess.serial_number == ESS_ANON_SN
    assert ess.model == "SPWR-Equinox-model"
    assert ess.last_report_date == SAMPLE_UNIX
    assert ess.power_3ph_kw == 0.326787
    assert ess.neg_lte_kwh == 7492.96582
    assert ess.pos_lte_kwh == 5672.499023
    assert ess.v1n_v == 122.489265
    assert ess.v2n_v == 122.489265
    assert ess.op_mode == "ENERGY_ARBITRAGE"
    assert ess.soc_val == 65.0
    assert ess.customer_soc_val == 59.0
    assert ess.soh_val == 100.0
    assert ess.t_invtr_degc == 36.619999
    assert ess.v_batt_v == 52.445
    assert ess.chrg_limit_pmax_kw == 10.762
    assert ess.dischrg_lim_pmax_kw == 10.004
    assert ess.max_t_batt_cell_degc == 30.059999
    assert ess.min_t_batt_cell_degc == 2.33
    assert ess.max_v_batt_cell_v == 3.28275
    assert ess.min_v_batt_cell_v == 3.27965


def test_pvs_firmware_setup_populates_auth_fields():
    """setup() loads serial, SSID, and LAN MAC from varserver paths."""

    async def request_var(path: str) -> Any:
        return {
            "/sys/info/serialnum": "ZT199999000000A0001",
            "/sys/info/ssid": "TestSiteSSID00",
            "/sys/info/lmac": "01:23:45:67:89:ab",
        }[path]

    fw = PVSFirmware(request_var)
    asyncio.run(fw.setup())
    assert fw.serial == "ZT199999000000A0001"
    assert fw.ssid == "TestSiteSSID00"
    assert fw.lmac == "01:23:45:67:89:ab"


def test_pvs_firmware_setup_keyerror_becomes_firmware_check_error():
    """Missing varserver key surfaces as PVSFirmwareCheckError."""

    async def request_var(path: str) -> Any:
        if path == "/sys/info/ssid":
            raise KeyError("/sys/info/ssid")
        return {
            "/sys/info/serialnum": "ZT199999000000A0001",
            "/sys/info/lmac": "01:23:45:67:89:ab",
        }[path]

    fw = PVSFirmware(request_var)
    with pytest.raises(PVSFirmwareCheckError):
        asyncio.run(fw.setup())
