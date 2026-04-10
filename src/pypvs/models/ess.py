"""Model for a Equinox ESS (Energy Storage System)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .varserver_coerce import float_var, str_var


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
        date_str = str_var(data, "msmtEps", "1970-01-01T00:00:00Z")
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=timezone.utc
            )
            last_report_date = int(dt.timestamp())
        except Exception:
            last_report_date = 0

        soc_val_scaled = float_var(data, "socVal", 0.0) * 100.0
        customer_soc_val_scaled = float_var(data, "customerSocVal", 0.0) * 100.0
        soh_val_scaled = float_var(data, "sohVal", 0.0) * 100.0

        return cls(
            serial_number=str_var(data, "sn"),
            model=str_var(data, "prodMdlNm"),
            last_report_date=last_report_date,
            power_3ph_kw=float_var(data, "p3phsumKw", 0.0),
            neg_lte_kwh=float_var(data, "negLtea3phsumKwh", 0.0),
            pos_lte_kwh=float_var(data, "posLtea3phsumKwh", 0.0),
            v1n_v=float_var(data, "v1nV", 0.0),
            v2n_v=float_var(data, "v2nV", 0.0),
            op_mode=str_var(data, "opMode"),
            soc_val=soc_val_scaled,
            customer_soc_val=customer_soc_val_scaled,
            soh_val=soh_val_scaled,
            t_invtr_degc=float_var(data, "tInvtrDegc", 0.0),
            v_batt_v=float_var(data, "vBattV", 0.0),
            chrg_limit_pmax_kw=float_var(data, "chrgLimitPmaxKw", 0.0),
            dischrg_lim_pmax_kw=float_var(data, "dischrgLimPmaxKw", 0.0),
            max_t_batt_cell_degc=float_var(data, "maxTBattCellDegc", 0.0),
            min_t_batt_cell_degc=float_var(data, "minTBattCellDegc", 0.0),
            max_v_batt_cell_v=float_var(data, "maxVBattCellV", 0.0),
            min_v_batt_cell_v=float_var(data, "minVBattCellV", 0.0),
        )
