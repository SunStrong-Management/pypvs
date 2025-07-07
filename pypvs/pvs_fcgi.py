import base64
import logging

_LOGGER = logging.getLogger(__name__)

class PVSFCGIClientLoginError(Exception):
    """ Exception raised when login to the PVS fails """

class PVSFCGIClientPostError(Exception):
    """ Exception raised when POST request to the PVS fails """

class PVSFCGIClient:
    def __init__(self, session, auth_user=None, auth_password=None):
        self.session = session
        self.auth_user = auth_user
        self.auth_password = auth_password
        self.pvs_details = None
        self._pvs_url: str | None = None
        self.login_endpoint = "/auth?login"
        self.cookies = None

    @property
    def pvs_url(self) -> str:
        return self._pvs_url

    @pvs_url.setter
    def pvs_url(self, value: str):
        self._pvs_url = value
        _LOGGER.debug(f"PVS URL set to {self._pvs_url}")

    def set_pvs_details(self, details):
        # check all fields are present
        if not all(
            key in details for key in ["serial"]
        ):
            raise ValueError(
                "PVS details must contain serial"
            )

        self.pvs_details = details
        _LOGGER.info(f"PVS details set: {self.pvs_details}")

    async def login_basic(self):
        if not self.auth_user:
            raise PVSFCGIClientLoginError("Auth user must be set before logging in.")
        if not self.pvs_details or not self.pvs_details.get("serial"):
            raise PVSFCGIClientLoginError("PVS details must be set before logging in.")

        # The PVS uses basic authentication with the username and password
        auth_token = base64.b64encode(
            f"{self.auth_user}:{self.auth_password}".encode("utf-8")
        ).decode()
        headers = {"Authorization": f"basic {auth_token}"}
        await self.login(headers=headers)

    async def login(self, headers=None):
        """
        Log in to the server to start a session.
        Store the cookies for subsequent requests.
        """

        if not self._pvs_url:
            raise PVSFCGIClientLoginError("PVS URL must be set before logging in.")

        login_url = f"{self._pvs_url}{self.login_endpoint}"

        _LOGGER.debug(f"Logging in to {login_url} with headers: {headers}")
        # TODO: Ignore certificate errors for now
        async with self.session.get(login_url, headers=headers, ssl=False) as response:
            if response.status != 200:
                raise PVSFCGIClientLoginError(
                    f"Login failed with status code: {response.status} and response: {response.text}"
                )

            self.cookies = response.cookies
            _LOGGER.info(f"Login successful! with cookies: {self.cookies}")

    async def _post_internal(self, url, payload_str):
        # TODO: Ignore certificate errors for now
        async with self.session.post(
            url, cookies=self.cookies, data=payload_str, ssl=False
        ) as response:
            response_text = await response.text()
            # FIXME: The server retunrs 500 or 200 with empty response when the session is invalid
            if response.status == 200:
                _LOGGER.debug("POST request successful!")
                return await response.json()
            elif response.status in [400, 401, 500]:
                raise PVSFCGIClientLoginError("Unauthorized access (missing cookie). Retry login!")
            else:
                raise PVSFCGIClientPostError(
                    f"POST request failed with status code: {response.status}"
                )

    async def execute_post_request(self, endpoint, params=None):
        """
        Execute a POST request using the stored cookies.
        This function uses lazy authentication.
        If the server responds with a 401 (Unauthorized) or
        400 (Bad Request) for missing session id (i.e. the cookie)
        the client will try getting a new session id and retry the request.

        Args:
            - endpoint (str): The relative URL for the POST request.
            - params (dict): Optional query parameters for the POST request.

        Returns:
            - Response data in JSON format if successful.
        """
        if not self._pvs_url:
            raise PVSFCGIClientPostError("PVS URL must be set before making POST requests.")

        url = f"{self._pvs_url}{endpoint}"
        payload_str = "".join([f"{key}={value}" for key, value in params.items()])
        _LOGGER.debug(
            f"POST request to {url} with payload: {payload_str} and cookies: {self.cookies}"
        )

        # First try our luck if the session is still valid
        try:
            return await self._post_internal(url, payload_str)
        except PVSFCGIClientLoginError:
            _LOGGER.warning("Unauthorized access. Retrying login...")

        # Retry login to refresh the session cookies
        await self.login_basic()

        # Retry the request after re-authentication
        return await self._post_internal(url, payload_str)
