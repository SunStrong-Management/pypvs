"""Model for the PVS itself as a gateway."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class PVSGateway:
    """Model for the PVS itself as a gateway."""

    model: str
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

        model = data.get("/sys/info/sys_type").strip()
        rev = data.get("/sys/info/hwrev").strip()

        return cls(
            model=model,
            hardware_version=f"{model} {rev}",
            software_version=data.get("/sys/info/sw_rev"),
            uptime_s=float(data.get("/sys/info/uptime")),
            mac=data.get("/sys/info/lmac"),
            ram_usage_percent=int(data.get("/sys/info/ram_usage")),
            flash_usage_percent=int(data.get("/sys/info/flash_usage")),
            cpu_usage_percent=int(data.get("/sys/info/cpu_usage")),
        )
