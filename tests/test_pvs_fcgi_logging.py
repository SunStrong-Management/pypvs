"""Tests that the FCGI client does not log credentials."""

from __future__ import annotations

import asyncio
import base64
import logging
from http.cookies import SimpleCookie

from pypvs.pvs_fcgi import PVSFCGIClient

SERIAL = "ZT000000000000A1B2C"
PASSWORD = "A1B2C"
SESSION = "s3cr3tsessiontoken"


class FakeResponse:
    def __init__(self, status: int, body: str = "", cookies=None) -> None:
        self.status = status
        self._body = body
        self.cookies = cookies or SimpleCookie()

    async def __aenter__(self) -> FakeResponse:
        return self

    async def __aexit__(self, *args) -> None:
        return None

    async def text(self) -> str:
        return self._body


class FakeSession:
    def get(self, url, headers=None, ssl=None) -> FakeResponse:
        cookies = SimpleCookie()
        cookies["session"] = SESSION
        return FakeResponse(200, cookies=cookies)

    def post(self, url, cookies=None, data=None, ssl=None) -> FakeResponse:
        return FakeResponse(200, '{"values": []}')


def test_login_and_request_do_not_log_credentials(caplog) -> None:
    client = PVSFCGIClient(FakeSession(), auth_user="ssm_owner", auth_password=PASSWORD)
    client.pvs_url = "https://192.0.2.1"

    with caplog.at_level(logging.DEBUG, logger="pypvs"):
        client.set_pvs_details({"serial": SERIAL})
        asyncio.run(client.execute_post_request("/vars", params={"match": "info"}))

    auth = base64.b64encode(f"ssm_owner:{PASSWORD}".encode()).decode()
    assert "Login successful" in caplog.text
    for secret in (PASSWORD, auth, SESSION, SERIAL):
        assert secret not in caplog.text
