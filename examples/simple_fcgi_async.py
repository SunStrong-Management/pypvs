# This example demonstrates how to use the PVSFCGIClient class to
# interact with a SunStrong Management PVS6 gateway using basic authentication.
#

import asyncio
import logging
import os

import aiohttp

from pypvs.pvs_fcgi import PVSFCGIClient

logging.basicConfig(level=logging.DEBUG)


# Example
async def main():
    async with aiohttp.ClientSession() as session:
        # Get PVS serial number from environment variable
        pvs_serial = os.getenv("PVS_SN")
        if pvs_serial is None:
            print(
                "Please set the PVS_SN environment variable with the PVS serial number."
            )
        # The username is: ssm_owner
        # The password is: the last 5 characters of the PVS serial number
        client = PVSFCGIClient(
            session, auth_user="ssm_owner", auth_password=pvs_serial[-5:]
        )
        # Get PVS host from environment variable
        host = os.getenv("PVS_HOST")
        if host is None:
            print("Please set the PVS_HOST environment variable with the PVS IP.")
        client.pvs_url = f"http://{host}"  # PVS URL with configurable host

        # Use basic authentication with the username and password
        client.set_pvs_details({"serial": pvs_serial})

        # We don't need to call login_basic() because refresh of the session cookies
        # is handled automatically by the PVSFCGIClient class.
        # await client.login_basic()

        response = await client.execute_post_request(
            "/vars", params={"name": "/sys/info/uptime"}
        )
        print(f"Response: {response}")


if __name__ == "__main__":
    asyncio.run(main())
