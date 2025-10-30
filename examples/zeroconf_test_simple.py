import socket

from zeroconf import ServiceBrowser, Zeroconf


class MyListener:

    def remove_service(self, zeroconf, type, name):
        print(f"Service {name} removed")

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info:
            print(
                f"Service {name} added, IP address: {socket.inet_ntoa(info.addresses[0])} port {info.port}"
            )

    def update_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info:
            print(
                f"Service {name} update, IP address: {socket.inet_ntoa(info.addresses[0])} port {info.port}"
            )


zeroconf = Zeroconf()
listener = MyListener()
browser = ServiceBrowser(zeroconf, "_pvs6._tcp.local.", listener)
try:
    input("Press enter to exit...\n\n")
finally:
    zeroconf.close()
