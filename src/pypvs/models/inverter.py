"""Model for an Enphase microinverter."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class PVSInverter:
    """Model for an Enphase microinverter."""

    serial_number: str
    model: str
    last_report_date: int
    last_report_kw: float
    last_report_voltage_v: float
    last_report_current_a: float
    last_report_frequency_hz: float
    last_report_temperature_c: float
    lte_kwh: float

    @classmethod
    def from_varserver(cls, data: dict[str, Any]) -> PVSInverter:
        """
        Initialize from /sys/devices/inverter/*/* varserver variables packed in JSON.
        """

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
        )
