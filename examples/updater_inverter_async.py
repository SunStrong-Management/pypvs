# This is an example of how to use a PVS updater to get data
#

import os
import asyncio
import aiohttp

from pypvs.pvs import PVS
from pypvs.updaters.production_inverters import PVSProductionInvertersUpdater
from pypvs.models.pvs import PVSData
from pypvs.models.common import CommonProperties
from pypvs.const import SupportedFeatures
from pypvs.exceptions import ENDPOINT_PROBE_EXCEPTIONS

import logging

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
        inverter_updater = PVSProductionInvertersUpdater(
            pvs.getVarserverVar, pvs.getVarserverVars, common_properties
        )

        discovered_features = SupportedFeatures(0)
        inverter_is_there = await inverter_updater.probe(discovered_features)
        if not inverter_is_there:
            print("No inverters found for that PVS on varserver")
            return

        # setup a periodic task to fetch data every 5 seconds
        pvs_data = PVSData()
        while True:
            await inverter_updater.update(pvs_data)

            print(">>>>>> Inverters:")
            for inverter in pvs_data.inverters.values():
                print(f"{inverter.serial_number}: {inverter}")

            await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exiting...")
