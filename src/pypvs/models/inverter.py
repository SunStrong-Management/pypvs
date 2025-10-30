"""Model for an Enphase microinverter."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional


@dataclass(slots=True)
class PVSInverter:
    """
    Model for an Enphase microinverter.

    Attributes:
        serial_number (str): The serial number of the inverter.
        model (str): The model name or number of the inverter.
        last_report_date (Optional[datetime | str]): The timestamp of the
            last report, as a datetime object or string.
        last_report_kw (Optional[float]): The last reported AC power
            output in kilowatts.
        last_report_voltage_v (Optional[float]): The last reported AC
            voltage in volts.
        last_report_current_a (Optional[float]): The last reported AC
            current in amperes.
        last_report_frequency_hz (Optional[float]): The last reported AC
            frequency in hertz.
        last_report_temperature_c (Optional[float]): The last reported
            temperature in degrees Celsius.
        lte_kwh (Optional[float]): The lifetime energy produced by the
            inverter in kilowatt-hours.
        last_mppt_voltage_v (Optional[float]): The DC voltage from the panel.
        last_mppt_current_a (Optional[float]): The DC current from the panel.
        last_mppt_power_kw (Optional[float]): The DC power from the panel.

    Methods:
        from_varserver(data: dict[str, Any]) -> PVSInverter:
            Class method to initialize a PVSInverter instance from a
            dictionary of varserver variables.
            Converts the date string in ISO 8601 format to a UTC timestamp.
    """

    serial_number: str
    model: str
    last_report_date: Optional[datetime | str] = None
    last_report_kw: Optional[float] = None
    last_report_voltage_v: Optional[float] = None
    last_report_current_a: Optional[float] = None
    last_report_frequency_hz: Optional[float] = None
    last_report_temperature_c: Optional[float] = None
    lte_kwh: Optional[float] = None
    last_mppt_voltage_v: Optional[float] = None
    last_mppt_current_a: Optional[float] = None
    last_mppt_power_kw: Optional[float] = None

    @classmethod
    def from_varserver(cls, data: dict[str, Any]) -> PVSInverter:
        """Initialize from /sys/devices/inverter/*/* varserver variables
        packed in JSON to a PVSInverter instance."""

        # Convert date from format "2024-09-30T16:15:00Z" to UTC seconds
        date_str = data["msmtEps"]
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc
        )
        last_report_date = int(dt.timestamp())

        return cls(
            serial_number=data["sn"],
            model=data["prodMdlNm"],
            last_report_date=last_report_date,
            last_report_kw=data["p3phsumKw"],
            last_report_voltage_v=data["vln3phavgV"],
            last_report_current_a=data["i3phsumA"],
            last_report_frequency_hz=data["freqHz"],
            last_report_temperature_c=data["tHtsnkDegc"],
            lte_kwh=data["ltea3phsumKwh"],
            last_mppt_voltage_v=data.get("vMppt1V"),
            last_mppt_current_a=data.get("iMppt1A"),
            last_mppt_power_kw=data.get("pMppt1Kw"),
        )
