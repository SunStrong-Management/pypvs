import asyncio
from zeroconf import Zeroconf, ServiceBrowser
from aiohttp import ClientSession
from typing import Optional
import socket

from pypvs.pvs import PVS


class DeviceListener:
    def __init__(self, target_hostname: str):
        self.target_hostname = target_hostname
        self.ip_address: Optional[str] = None

    def remove_service(self, zeroconf, type, name):
        pass

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        print(f"Service {name} added, info: {info}")
        if info and info.server == self.target_hostname:
            addresses = info.addresses
            for address in addresses:
                ip_address = socket.inet_ntoa(address)
                print(f"Service {name} added, IP address: {ip_address}")
                # take the first IP address
                if not self.ip_address:
                    self.ip_address = ip_address
                    # TODO: not super clear on how to run async code here
                    asyncio.run(self.discover_a_pvs(self.ip_address))

    def update_service(self, zeroconf, type, name):
        self.add_service(zeroconf, type, name)

    async def discover_a_pvs(self, ip_address: str):
        async with ClientSession() as session:
            pvs = PVS(session=session, host=ip_address)
            await pvs.validate()

            # print pvs details
            print(f"Serial number: {pvs.serial_number}")
            print(f"MAC address: {pvs._firmware.lmac}")


async def main():
    print("This script has to be running when the PVS registers.")

    # Create zeroconf object and listener
    zeroconf = Zeroconf()
    listener = DeviceListener(target_hostname="pvs6.local.")

    # Start service browser
    ServiceBrowser(zeroconf, "_pvs6._tcp.local.", listener)

    try:
        # Keep running indefinitely until stopped by Ctrl+C
        print("Listening for services... Press Ctrl+C to stop.")
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        zeroconf.close()


if __name__ == "__main__":
    asyncio.run(main())
