class PVSError(Exception):
    """Base class for PVS exceptions."""


class PVSFirmwareCheckError(PVSError):
    """Exception raised when unable to query the PVS firmware version."""


class PVSAuthenticationError(PVSError):
    """Exception raised when unable to get a session if from the PVS."""


class PVSProbeFailed(PVSError):
    """Exception raised when the PVS probe fails."""


class PVSCommunicationError(PVSError):
    """Exception raised when the PVS communication fails."""


class PVSDataFormatError(PVSError):
    """Exception raised when the PVS data format is incorrect."""


ENDPOINT_PROBE_EXCEPTIONS = (
    PVSDataFormatError,
    PVSAuthenticationError,
    PVSProbeFailed,
    PVSCommunicationError,
    KeyError,
)
