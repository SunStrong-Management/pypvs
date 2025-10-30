import asyncio
import socket
from typing import Optional

from aiohttp import ClientSession
from zeroconf import ServiceBrowser, Zeroconf

from pypvs.pvs import PVS


class DeviceListener:
    def __init__(self, target_hostnames: list[str]):
        self.target_hostnames = target_hostnames
        self.ip_address: Optional[str] = None

    def remove_service(self, zeroconf, type, name):
        pass

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        print(f"Service {name} added for type {type}, info: {info}")
        if info and info.server in self.target_hostnames:
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
        if type in ["_pvs._tcp", "_pvs5._tcp"]:
            self.add_service(zeroconf, type, name)
        else:
            self.remove_service(zeroconf, type, name)

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
    listener = DeviceListener(target_hostnames=["pvs6.local.", "pvs5.local."])

    # Start service browser
    ServiceBrowser(zeroconf, ["_pvs6._tcp.local.", "_pvs5._tcp.local."], listener)

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
