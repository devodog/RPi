import network
from helpers import *

wlan = network.WLAN(network.STA_IF)

def connect_wifi(config):
    wlan.active(True)
    wlan.connect(config["wifi"]["SSID"], config["wifi"]["PASSWORD"])
    return wlan


async def maintain_wifi_connection():
    while True:
        if not wlan.isconnected():
            output("WiFi disconnected. Attempting reconnection...")
            try:
                connect_wifi(read_config())
                await asyncio.sleep(4)
                if wlan.isconnected():
                    output("WiFi reconnected!")
                    output("IP Address: ", wlan.ifconfig()[0])
                    sync_time()
                else:
                    output("Reconnection attempt failed. Trying again in 30 seconds")
            except Exception as e:
                output("Error during WiFi reconnection:", str(e))
        await asyncio.sleep(30)  # Check every 30 seconds
