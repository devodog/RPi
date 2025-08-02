import network
from helpers import *

wlan = network.WLAN(network.STA_IF)

def connect_wifi(config):
    wlan.active(True)
    wlan.connect(config["wifi"]["SSID"], config["wifi"]["PASSWORD"])
    return wlan


async def maintain_wifi_connection():
    while True:
        config = read_config()
        attempts = config["wifi"]["attempts"]
        frequency = config["wifi"]["freq"]

        if not wlan.isconnected():
            count = 1  # reset every disconnection cycle
            while count <= attempts:
                output("WiFi disconnected. Attempting reconnection...")
                try:
                    connect_wifi(config)
                    await asyncio.sleep(4)
                    if wlan.isconnected():
                        output("WiFi reconnected!")
                        output("IP Address: ", wlan.ifconfig()[0])
                        sync_time()
                        break  # exit retry loop
                    else:
                        output(f"{count} reconnection attempt(s) failed. Trying again...")
                except Exception as e:
                    output("Error during WiFi reconnection:", str(e))
                count += 1
            if not wlan.isconnected():
                output(f"WiFi still disconnected after {attempts} reconnection attempts.\n" \
                       f"Trying again in {frequency}min.")
        await asyncio.sleep(frequency * 60)

