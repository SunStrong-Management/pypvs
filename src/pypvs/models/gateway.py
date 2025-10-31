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
    uptime_s: int
    mac: str
    ram_usage_percent: int
    flash_usage_percent: int
    cpu_usage_percent: int

    @classmethod
    def from_varserver(cls, data: dict[str, Any]) -> PVSGateway:
        """Initialize from a /sys/info varserver variables"""

        return cls(
            model=data["/sys/info/sys_type"].strip(),
            hardware_version=data["/sys/info/model"] + " " + data["/sys/info/hwrev"],
            software_version=data["/sys/info/sw_rev"],
            uptime_s=data["/sys/info/uptime"],
            mac=data["/sys/info/lmac"],
            ram_usage_percent=data["/sys/info/ram_usage"],
            flash_usage_percent=data["/sys/info/flash_usage"],
            cpu_usage_percent=data["/sys/info/cpu_usage"],
        )
