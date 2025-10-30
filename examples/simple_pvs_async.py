# This is an example of how to use the PVS class to get data
# from a SunStrong Management PVS6 gateway using asyncio.
#

import os
import time
import asyncio
import aiohttp
import logging

from pypvs.pvs import PVS
from pypvs.exceptions import ENDPOINT_PROBE_EXCEPTIONS

logging.basicConfig(level=logging.DEBUG)


async def fetch_data(pvs):
    # get the uptime
    uptime = await pvs.getVarserverVar("/sys/info/uptime")
    # print both the uptime and the local time
    print(f">>>>>> Uptime: {uptime}, Local time: {time.time()}")

    livedata = await pvs.getVarserverVars("/sys/livedata")
    # print livedata well formatted
    print(">>>>>> LiveData:")
    for key, value in livedata.items():
        print(f"{key}: {value}")


# Example
async def main():
    # Get PVS host from environment variable
    host = os.getenv("PVS_HOST")
    if host is None:
        print("Please set the PVS_HOST environment variable with the PVS IP.")

    async with aiohttp.ClientSession() as session:
        pvs = PVS(session=session, host=host, user="ssm_owner")
        try:
            await pvs.discover()
            pvs_serial = pvs.serial_number
            # The password is the last 5 characters of the PVS serial number
            pvs_password = pvs_serial[-5:]
            await pvs.setup(auth_password=pvs_password)
            logging.info(f"Connected to PVS with serial: {pvs_serial}")
        except ENDPOINT_PROBE_EXCEPTIONS as e:
            logging.error(f"Cannot communicate with the PVS: {e}")
            return

        # setup a periodic task to fetch data every 5 seconds
        while True:
            await fetch_data(pvs)
            await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exiting...")
