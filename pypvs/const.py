import enum

# System Production
VARS_MATCH_INVERTERS = "/sys/devices/inverter/"
VARS_MATCH_METERS = "/sys/devices/meter/"
VARS_MATCH_INFO = "/sys/info"
VAR_UPTIME = "/sys/info/uptime"

class SupportedFeatures(enum.IntFlag):
    """Features available from the PVS. Features form a bitmask."""

    GATEWAY = 1  #: The PVS itself is the gateway
    INVERTERS = 2  #: PVS reports inverters
    METERING = 4  #: PVS reports active production meter

# TODO: fix until moved to Python 3.11
class StrEnum(str, enum.Enum):
    """Enum with string values."""
    pass


class PhaseNames(StrEnum):
    PHASE_1 = "L1"
    PHASE_2 = "L2"
    PHASE_3 = "L3"


PHASENAMES: list[str] = list(PhaseNames)
