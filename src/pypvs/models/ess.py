"""Model for a Equinox ESS (Energy Storage System)."""

from __future__ import annotations

from datetime import datetime, timezone

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class PVSESS:
    """Model for a Equinox ESS (Energy Storage System)."""

    serial_number: str
    model: str
    last_report_date: int
    power_3ph_kw: float
    neg_lte_kwh: float
    pos_lte_kwh: float
    v1n_v: float
    v2n_v: float
    op_mode: str = ""
    soc_val: float = 0.0
    customer_soc_val: float = 0.0
    soh_val: int = 0
    t_invtr_degc: float = 0.0
    v_batt_v: float = 0.0
    chrg_limit_pmax_kw: float = 0.0
    dischrg_lim_pmax_kw: float = 0.0
    max_t_batt_cell_degc: float = 0.0
    min_t_batt_cell_degc: float = 0.0
    max_v_batt_cell_v: float = 0.0
    min_v_batt_cell_v: float = 0.0

    @classmethod
    def from_varserver(cls, data: dict[str, Any]) -> PVSESS:
        """Initialize from /sys/devices/ess/*/* varserver variables packed in JSON."""

        # Convert date from format "2024-09-30T16:15:00Z" to UTC seconds
        date_str = data.get("msmtEps", "1970-01-01T00:00:00Z")
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            last_report_date = int(dt.timestamp())
        except Exception:
            last_report_date = 0

        return cls(
                serial_number=data.get("sn", ""),
                model=data.get("prodMdlNm", ""),
                last_report_date=last_report_date,
                power_3ph_kw=float(data.get("p3phsumKw", 0.0)),
                neg_lte_kwh=float(data.get("negLtea3phsumKwh", 0.0)),
                pos_lte_kwh=float(data.get("posLtea3phsumKwh", 0.0)),
                v1n_v=float(data.get("v1nV", 0.0)),
                v2n_v=float(data.get("v2nV", 0.0)),
                op_mode=data.get("opMode", ""),
                soc_val=float(data.get("socVal", 0.0)),
                customer_soc_val=float(data.get("customerSocVal", 0.0)),
                soh_val=int(data.get("sohVal", 0)),
                t_invtr_degc=float(data.get("tInvtrDegc", 0.0)),
                v_batt_v=float(data.get("vBattV", 0.0)),
                chrg_limit_pmax_kw=float(data.get("chrgLimitPmaxKw", 0.0)),
                dischrg_lim_pmax_kw=float(data.get("dischrgLimPmaxKw", 0.0)),
                max_t_batt_cell_degc=float(data.get("maxTBattCellDegc", 0.0)),
                min_t_batt_cell_degc=float(data.get("minTBattCellDegc", 0.0)),
                max_v_batt_cell_v=float(data.get("maxVBattCellV", 0.0)),
                min_v_batt_cell_v=float(data.get("minVBattCellV", 0.0)),
            )
