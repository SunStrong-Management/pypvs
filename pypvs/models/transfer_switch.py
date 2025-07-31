"""Model for a MIDC (Microgrid Interconnected Device Controller)."""

from __future__ import annotations

from datetime import datetime

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class PVSTransferSwitch:
    """Model for a MIDC (Microgrid Interconnected Device Controller)."""

    serial_number: str
    model: str
    last_report_date: int
    mid_state: str = ""
    pvd1_state: str = ""
    temperature_c: float = 0.0
    v1n_grid_v: float = 0.0
    v1n_v: float = 0.0
    v2n_grid_v: float = 0.0
    v2n_v: float = 0.0
    v_supply_v: float = 0.0

    @classmethod
    def from_varserver(cls, data: dict[str, Any]) -> "PVSTransferSwitch":
        """Initialize from /sys/devices/transfer_switch/*/* varserver variables packed in JSON."""
        date_str = data.get("msmtEps", "1970-01-01T00:00:00Z")
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
            last_report_date = int(dt.timestamp())
        except Exception:
            last_report_date = 0

        return cls(
            serial_number=data.get("sn", ""),
            model=data.get("prodMdlNm", ""),
            last_report_date=last_report_date,
            mid_state=data.get("midStEnum", ""),
            pvd1_state=data.get("pvd1StEnum", ""),
            temperature_c=float(data.get("tDegc", 0.0)),
            v1n_grid_v=float(data.get("v1nGridV", 0.0)),
            v1n_v=float(data.get("v1nV", 0.0)),
            v2n_grid_v=float(data.get("v2nGridV", 0.0)),
            v2n_v=float(data.get("v2nV", 0.0)),
            v_supply_v=float(data.get("vSpplyV", 0.0)),
        )
