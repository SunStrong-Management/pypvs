# This is an example of how to use the PVSWebSocket class to receive
# real-time live data from a SunStrong Management PVS6 gateway.
#
# The WebSocket provides faster updates than polling the HTTP API,
# typically pushing data every few seconds.

import asyncio
import logging
import os

from pypvs.pvs_websocket import PVSWebSocket

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)


def on_live_data_update(changed_vars: set[str]) -> None:
    """Callback when live data is updated."""
    _LOGGER.info(f"Data updated for: {changed_vars}")


async def main():
    # Get PVS host from environment variable
    host = os.getenv("PVS_HOST")
    if host is None:
        print("Please set the PVS_HOST environment variable with the PVS IP.")
        return

    # Create WebSocket client
    ws = PVSWebSocket(host=host)

    # Add listener for updates
    remove_listener = ws.add_listener(on_live_data_update)

    # Connect (starts background task with auto-reconnect)
    await ws.connect()
    _LOGGER.info(f"WebSocket connecting to {host}...")

    try:
        # Print live data every 5 seconds
        while True:
            await asyncio.sleep(5)

            live_data = ws.live_data
            if live_data is None:
                _LOGGER.info("Waiting for connection...")
                continue

            print("\n" + "=" * 50)
            print("Live Data:")
            print(f"  Timestamp:        {live_data.time}")
            print(f"  PV Power:         {live_data.pv_p} kW")
            print(f"  PV Energy:        {live_data.pv_en} kWh")
            print(f"  Net Power:        {live_data.net_p} kW")
            print(f"  Net Energy:       {live_data.net_en} kWh")
            print(f"  Site Load Power:  {live_data.site_load_p} kW")
            print(f"  Site Load Energy: {live_data.site_load_en} kWh")
            print(f"  ESS Power:        {live_data.ess_p} kW")
            print(f"  ESS Energy:       {live_data.ess_en} kWh")
            print(f"  Battery SOC:      {live_data.soc}%")
            print(f"  Backup Time:      {live_data.backup_time_remaining} min")
            print(f"  MIDC State:       {live_data.midstate}")
            print("=" * 50)

    except asyncio.CancelledError:
        pass
    finally:
        # Clean up
        remove_listener()
        await ws.disconnect()
        _LOGGER.info("Disconnected")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
