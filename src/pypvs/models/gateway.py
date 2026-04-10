"""Model for the PVS itself as a gateway."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .varserver_coerce import float_var, int_var, str_var


@dataclass(slots=True)
class PVSGateway:
    """Model for the PVS itself as a gateway."""

    model: str
    pvs_type: str
    hardware_version: str
    software_version: str
    uptime_s: float
    mac: str
    ram_usage_percent: int
    flash_usage_percent: int
    cpu_usage_percent: int

    @classmethod
    def from_varserver(cls, data: dict[str, Any]) -> PVSGateway:
        """Initialize from a /sys/info varserver variables"""

        pvs_model = str_var(data, "/sys/info/model").strip()
        hw_rev = str_var(data, "/sys/info/hwrev").strip()

        return cls(
            model=str_var(data, "/sys/info/sys_type").strip(),
            pvs_type=pvs_model,
            hardware_version=f"{pvs_model} {hw_rev}",
            software_version=str_var(data, "/sys/info/sw_rev"),
            uptime_s=float_var(data, "/sys/info/uptime", 0.0),
            mac=str_var(data, "/sys/info/lmac"),
            ram_usage_percent=int_var(data, "/sys/info/ram_usage", 0),
            flash_usage_percent=int_var(data, "/sys/info/flash_usage", 0),
            cpu_usage_percent=int_var(data, "/sys/info/cpu_usage", 0),
        )
