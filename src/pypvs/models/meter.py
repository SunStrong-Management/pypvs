"""Model for a built-in PVS meter."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True)
class PVSMeter:
    """Model for a built-in PVS meter."""

    serial_number: str
    model: str
    last_report_date: int
    power_3ph_kw: float
    voltage_3ph_v: float
    current_3ph_a: float
    freq_hz: float
    lte_3ph_kwh: float
    ct_scale_factor: float
    i1_a: float
    i2_a: float
    neg_lte_kwh: float
    net_lte_kwh: float
    p1_kw: float
    p2_kw: float
    pos_lte_kwh: float
    q3phsum_kvar: float
    s3phsum_kva: float
    tot_pf_ratio: float
    v12_v: float
    v1n_v: float
    v2n_v: float

    @classmethod
    def from_varserver(cls, data: dict[str, Any]) -> PVSMeter:
        """Initialize from /sys/devices/meter/*/* varserver variables packed in JSON."""

        # Convert date from format "2024-09-30T16:15:00Z" to UTC seconds
        date_str = data.get("msmtEps", "1970-01-01T00:00:00Z")
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=timezone.utc
            )
            last_report_date = int(dt.timestamp())
        except Exception:
            last_report_date = 0

        return cls(
            serial_number=data.get("sn", ""),
            model=data.get("prodMdlNm", ""),
            last_report_date=last_report_date,
            power_3ph_kw=float(data.get("p3phsumKw", 0.0)),
            voltage_3ph_v=float(data.get("vln3phavgV", 0.0)),
            current_3ph_a=float(data.get("i3phsumA", 0.0)),
            freq_hz=float(data.get("freqHz", 0.0)),
            lte_3ph_kwh=float(data.get("ltea3phsumKwh", 0.0)),
            ct_scale_factor=float(data.get("ctSclFctr", 1.0)),
            i1_a=float(data.get("i1A", 0.0)),
            i2_a=float(data.get("i2A", 0.0)),
            neg_lte_kwh=float(data.get("negLtea3phsumKwh", 0.0)),
            net_lte_kwh=float(data.get("netLtea3phsumKwh", 0.0)),
            p1_kw=float(data.get("p1Kw", 0.0)),
            p2_kw=float(data.get("p2Kw", 0.0)),
            pos_lte_kwh=float(data.get("posLtea3phsumKwh", 0.0)),
            q3phsum_kvar=float(data.get("q3phsumKvar", 0.0)),
            s3phsum_kva=float(data.get("s3phsumKva", 0.0)),
            tot_pf_ratio=float(data.get("totPfRto", 0.0)),
            v12_v=float(data.get("v12V", 0.0)),
            v1n_v=float(data.get("v1nV", 0.0)),
            v2n_v=float(data.get("v2nV", 0.0)),
        )
