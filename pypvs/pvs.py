import logging
from typing import Callable
import base64

from .pvs_fcgi import PVSFCGIClient, PVSFCGIClientPostError, PVSFCGIClientLoginError
from .exceptions import PVSError, PVSAuthenticationError, PVSProbeFailed, PVSCommunicationError, PVSDataFormatError

from .firmware import PVSFirmware
from .const import SupportedFeatures, VAR_UPTIME

from .updaters.base import PVSUpdater
from .updaters.gateway import PVSGatewayUpdater
from .updaters.production_inverters import PVSProductionInvertersUpdater

from .models.common import CommonProperties
from .models.pvs import PVSData


UPDATERS: list[type["PVSUpdater"]] = [
    PVSGatewayUpdater,
    PVSProductionInvertersUpdater
]

_LOGGER = logging.getLogger(__name__)

def register_updater(updater: type["PVSUpdater"]) -> Callable[[], None]:
    """Register an updater."""
    UPDATERS.append(updater)

    def _remove_updater() -> None:
        UPDATERS.remove(updater)

    return _remove_updater


def get_updaters() -> list[type[PVSUpdater]]:
    return UPDATERS


class PVS:
    def __init__(self, session, host=None, user="ssm_owner", password=None):
        self._host: str | None = None
        self._common_properties: CommonProperties = CommonProperties()

        self._firmware = PVSFirmware(self.getVarserverVar)
        self._supported_features: SupportedFeatures | None = None
        self._updaters: list[PVSUpdater] = []
        self.data: PVSData | None = None

        self.fcgi_client = PVSFCGIClient(session=session, auth_user=user, auth_password=password)
        self.host = host

    def update_clients(self):
        self.fcgi_client.pvs_url = f"https://{self.host}"

    async def getVarserver(self, endpoint, params=None):
        try:
            response_data = await self.fcgi_client.execute_post_request(endpoint, params=params)
            _LOGGER.debug(f"Received response: {response_data}")
            return response_data
        except PVSFCGIClientPostError as e:
            raise PVSCommunicationError("POST request failed")
        except PVSFCGIClientLoginError as e:
            raise PVSAuthenticationError("Login to the PVS failed")
        except Exception as e:
            raise PVSError("General error")

    async def getVarserverVar(self, varname):
        response_data = await self.getVarserver("/vars", params={"name": varname})

        try:
            # sample return: {'values': [{'name': '/sys/info/uptime', 'value': '106408.20'}], 'count': 1}
            value = response_data["values"][0]["value"]
            _LOGGER.debug(f"Received {varname}: {value}")
            return response_data["values"][0]["value"]
        except KeyError as e:
            raise PVSDataFormatError("Cannot extract value from response {response_data}")

    async def getVarserverVars(self, match):
        response_data = await self.getVarserver("/vars", params={"match": match})

        try:
            # construct a new dictionary with the varname as the key and the value as the value
            value_dict = {}
            for item in response_data["values"]:
                value_dict[item["name"]] = item["value"]
            _LOGGER.debug(f"Received {len(value_dict)} values: {value_dict}")
            return value_dict
        except KeyError as e:
            raise PVSDataFormatError("Cannot construct dictionary from response {response_data}")

    async def discover(self) -> None:
        """Discover the PVS and its capabilities."""
        await self._firmware.setup()
        self.fcgi_client.set_pvs_details({
            "serial": self._firmware.serial
        })

    async def setup(self, auth_password: str = None) -> None:
        if not self._firmware.serial:
            await self.discover()

        if auth_password:
            # set the password for the PVS
            self.fcgi_client.auth_password = auth_password

        try:
            await self.getVarserverVar(VAR_UPTIME)
        except PVSFCGIClientPostError as e:
            raise PVSAuthenticationError("Login failed on setup")

    def generate_client_reference_id(self):
        """Generate a client reference id according to the specified rules."""

        # cannot generate without a serial number
        if not self._firmware.serial:
            raise PVSAuthenticationError("Cannot generate client reference id without a serial number")

        # generate the client_reference_id
        client_reference_id = base64.b64encode(f"{self._firmware.serial}:{self._token_secret}".encode()).decode()
        # finally apply a workaround for the base64 encoding to be accepter by the server
        return client_reference_id.replace("=", "-")

    async def validate(self) -> bool:
        # just try to read some variables to see if the connection to the PVS is ok
        await self._firmware.setup()
        return True

    async def probe(self) -> None:
        """Probe for model and supported features."""
        supported_features = SupportedFeatures(0)
        updaters: list[PVSUpdater] = []
        self._common_properties.reset_probe_properties()

        for updater in get_updaters():
            klass = updater(
                request_var=self.getVarserverVar,
                request_vars=self.getVarserverVars,
                common_properties=self._common_properties
            )
            if updater_features := await klass.probe(supported_features):
                supported_features |= updater_features
                updaters.append(klass)

        if not supported_features & SupportedFeatures.GATEWAY:
            raise PVSProbeFailed("Unable to find gateway information")

        self._updaters = updaters
        self._supported_features = supported_features

    async def update(self) -> PVSData:
        """Update data."""
        if not self._supported_features:
            await self.probe()

        data = PVSData()
        for updater in self._updaters:
            await updater.update(data)

        self.data = data
        return data

    @property
    def host(self) -> str:
        """Return the PVS host."""
        return self._host

    @host.setter
    def host(self, value: str):
        self._host = value
        if self._host:
            self.update_clients()

    @property
    def serial_number(self) -> str | None:
        """Return the PVS serial number."""
        return self._firmware.serial

    @property
    def supported_features(self) -> SupportedFeatures:
        """Return the supported features."""
        assert self._supported_features is not None, "Call setup() first"  # nosec
        return self._supported_features
