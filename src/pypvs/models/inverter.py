"""Model for an Enphase microinverter."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from .varserver_coerce import float_var, str_var


@dataclass(slots=True)
class PVSInverter:
    """
    Model for an Enphase microinverter.

    Attributes:
        serial_number (str): The serial number of the inverter.
        model (str): The model name or number of the inverter.
        last_report_date (Optional[int]): The timestamp of the
            last report in UTC seconds.
        last_report_kw (Optional[float|str]): The last reported AC power
            output in kilowatts.
        last_report_voltage_v (Optional[float|str]): The last reported AC
            voltage in volts.
        last_report_current_a (Optional[float|str]): The last reported AC
            current in amperes.
        last_report_frequency_hz (Optional[float|str]): The last reported AC
            frequency in hertz.
        last_report_temperature_c (Optional[float|str]): The last reported
            temperature in degrees Celsius.
        lte_kwh (Optional[float|str]): The lifetime energy produced by the
            inverter in kilowatt-hours.
        last_mppt_voltage_v (Optional[float|str]): The DC voltage from the panel.
        last_mppt_current_a (Optional[float|str]): The DC current from the panel.
        last_mppt_power_kw (Optional[float|str]): The DC power from the panel.

    Methods:
        from_varserver(data: dict[str, Any]) -> PVSInverter:
            Class method to initialize a PVSInverter instance from a
            dictionary of varserver variables.
            Converts the date string in ISO 8601 format to a UTC timestamp.
    """

    serial_number: str
    model: str
    last_report_date: Optional[int] = None
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

        date_str = str_var(data, "msmtEps", "1970-01-01T00:00:00Z")
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=timezone.utc
            )
            last_report_date = int(dt.timestamp())
        except Exception:
            last_report_date = 0

        return cls(
            serial_number=str_var(data, "sn"),
            model=str_var(data, "prodMdlNm"),
            last_report_date=last_report_date,
            last_report_kw=float_var(data, "p3phsumKw", 0.0),
            last_report_voltage_v=float_var(data, "vln3phavgV", 0.0),
            last_report_current_a=float_var(data, "i3phsumA", 0.0),
            last_report_frequency_hz=float_var(data, "freqHz", 0.0),
            last_report_temperature_c=float_var(data, "tHtsnkDegc", 0.0),
            lte_kwh=float_var(data, "ltea3phsumKwh", 0.0),
            last_mppt_voltage_v=float_var(data, "vMppt1V", 0.0),
            last_mppt_current_a=float_var(data, "iMppt1A", 0.0),
            last_mppt_power_kw=float_var(data, "pMppt1Kw", 0.0),
        )
