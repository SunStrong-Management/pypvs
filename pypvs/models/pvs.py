"""Model for an PVS."""

from dataclasses import dataclass, field
from typing import Any

from .inverter import PVSInverter
from .meter import PVSMeter
from .ess import PVSESS
from .transfer_switch import PVSTransferSwitch

@dataclass(slots=True)
class PVSData:
    """Model for a PVS6."""
    gateway: dict[str, Any] = field(default_factory=dict)

    inverters: dict[str, PVSInverter] = field(default_factory=dict)

    meters: dict[str, PVSMeter] = field(default_factory=dict)

    ess: dict[str, PVSESS] = field(default_factory=dict)

    transfer_switches: dict[str, PVSTransferSwitch] = field(default_factory=dict)

    # Raw data is exposed so we can __eq__ the data to see if
    # anything has changed and consumers of the library can
    # avoid dispatching data if nothing has changed.
    raw: dict[str, Any] = field(default_factory=dict)
