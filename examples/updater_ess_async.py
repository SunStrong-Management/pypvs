# This is an example of how to use a PVS updater to get data
#

import asyncio
import logging
import os

import aiohttp

from pypvs.const import SupportedFeatures
from pypvs.exceptions import ENDPOINT_PROBE_EXCEPTIONS
from pypvs.models.common import CommonProperties
from pypvs.models.pvs import PVSData
from pypvs.pvs import PVS
from pypvs.updaters.ess import PVSESSUpdater

logging.basicConfig(level=logging.DEBUG)


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

        common_properties = CommonProperties()
        ess_updater = PVSESSUpdater(
            pvs.getVarserverVar, pvs.getVarserverVars, common_properties
        )

        discovered_features = SupportedFeatures(0)
        ess_is_there = await ess_updater.probe(discovered_features)
        if not ess_is_there:
            print("No ESS found for that PVS on varserver")
            return

        # setup a periodic task to fetch data every 5 seconds
        pvs_data = PVSData()
        while True:
            await ess_updater.update(pvs_data)

            print(">>>>>> ESS:")
            for ess in pvs_data.ess.values():
                print(f"{ess.serial_number}: {ess}")

            await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exiting...")
