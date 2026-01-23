"""Model for PVS live data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

# Mapping from varserver path to attribute name
_VAR_PATH_TO_ATTR: dict[str, str] = {
    "/sys/livedata/time": "time",
    "/sys/livedata/pv_p": "pv_p",
    "/sys/livedata/pv_en": "pv_en",
    "/sys/livedata/net_p": "net_p",
    "/sys/livedata/net_en": "net_en",
    "/sys/livedata/site_load_p": "site_load_p",
    "/sys/livedata/site_load_en": "site_load_en",
    "/sys/livedata/ess_en": "ess_en",
    "/sys/livedata/ess_p": "ess_p",
    "/sys/livedata/soc": "soc",
    "/sys/livedata/backupTimeRemaining": "backup_time_remaining",
    "/sys/livedata/midstate": "midstate",
}


@dataclass(slots=True)
class PVSLiveData:
    """Container for PVS live data values.

    Attributes:
        time: Timestamp of the live data reading
        pv_p: Solar production power in kW
        pv_en: Solar production energy in kWh
        net_p: Net grid power in kW (positive = importing, negative = exporting)
        net_en: Net grid energy in kWh
        site_load_p: Site load power in kW
        site_load_en: Site load energy in kWh
        ess_en: Battery energy in kWh
        ess_p: Battery power in kW (positive = discharging, negative = charging)
        soc: Battery state of charge percentage
        backup_time_remaining: Estimated backup time remaining in minutes
        midstate: MIDC transfer switch state
    """

    time: datetime | None = None
    pv_p: float | None = None
    pv_en: float | None = None
    net_p: float | None = None
    net_en: float | None = None
    site_load_p: float | None = None
    site_load_en: float | None = None
    ess_en: float | None = None
    ess_p: float | None = None
    soc: float | None = None
    backup_time_remaining: float | None = None
    midstate: str | None = None

    def get(self, var_name: str) -> Any:
        """Get value by varserver path.

        Args:
            var_name: The varserver path (e.g., "/sys/livedata/pv_p")

        Returns:
            The value for that path, or None if not found
        """
        attr = _VAR_PATH_TO_ATTR.get(var_name)
        if attr:
            return getattr(self, attr, None)
        return None

    @classmethod
    def from_varserver(cls, data: dict[str, Any]) -> PVSLiveData:
        """Initialize from /sys/livedata/* varserver variables.

        Args:
            data: Dictionary with varserver paths as keys

        Returns:
            PVSLiveData instance with parsed values
        """
        return cls(
            time=cls._parse_timestamp(data.get("/sys/livedata/time")),
            pv_p=cls._parse_numeric(data.get("/sys/livedata/pv_p")),
            pv_en=cls._parse_numeric(data.get("/sys/livedata/pv_en")),
            net_p=cls._parse_numeric(data.get("/sys/livedata/net_p")),
            net_en=cls._parse_numeric(data.get("/sys/livedata/net_en")),
            site_load_p=cls._parse_numeric(data.get("/sys/livedata/site_load_p")),
            site_load_en=cls._parse_numeric(data.get("/sys/livedata/site_load_en")),
            ess_en=cls._parse_numeric(data.get("/sys/livedata/ess_en")),
            ess_p=cls._parse_numeric(data.get("/sys/livedata/ess_p")),
            soc=cls._parse_numeric(data.get("/sys/livedata/soc")),
            backup_time_remaining=cls._parse_numeric(
                data.get("/sys/livedata/backupTimeRemaining")
            ),
            midstate=data.get("/sys/livedata/midstate"),
        )

    @staticmethod
    def _parse_numeric(value: Any) -> float | None:
        """Parse a numeric value from varserver response."""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            if value.lower() in ("nan", "null", ""):
                return None
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        return None

    @staticmethod
    def _parse_timestamp(value: Any) -> datetime | None:
        """Parse a timestamp value from varserver response.

        Handles both Unix seconds and milliseconds formats.
        """
        if value is None:
            return None
        try:
            timestamp = int(value) if isinstance(value, str) else int(value)
            current_time = datetime.now(timezone.utc).timestamp()

            # Detect milliseconds vs seconds
            if timestamp > current_time + (365 * 24 * 3600):
                timestamp = timestamp / 1000

            # Validate
            if timestamp < 0 or timestamp > current_time + (365 * 24 * 3600):
                return None

            return datetime.fromtimestamp(timestamp, tz=timezone.utc)
        except (ValueError, TypeError, OSError):
            return None
