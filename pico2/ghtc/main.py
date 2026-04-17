# main.py - Main entry point for the Raspberry Pi Pico W application
from wifi import *
from helpers import *
from publish import send_data
from command_handler import read
from machine import Pin
import time

# LED Hart beat...
hb = Pin("LED", Pin.OUT)

# Set up UART interrupt
Pin(1).irq(read, trigger=Pin.IRQ_FALLING)

ascii_art = (
    "     .----------------.\r\n"
    "    |   Raspberry Pi   |\r\n"
    "    |      Pico W      |\r\n"
    "    |  .------------.  |\r\n"
    "    |  | [] [] [] []|  |\r\n"
    "    |  | [] [] [] []|  |\r\n"
    "    |  '------------'  |\r\n"
    "    |____version 2.1 __|\r\n"
    "      |  || GREEN ||  |\r\n"
    "      |  || HOUSE ||  |\r\n"
    "      '--------------'\r\n"
)
output("START\r\n")
cmd_output(ascii_art, "")

async def main():
    # Attempt initial connection (non-blocking success not critical)
    try:
        output(f"Attempting to connect to WiFi using the following config:\r\nSSID: {read_config()['wifi']['SSID']}, PASSWORD: {read_config()['wifi']['PASSWORD']}")
        connect_wifi(read_config())
        time.sleep(4)
        if wlan.isconnected():
            output("WiFi connected!")
            output("IP Address: ", wlan.ifconfig()[0])
            sync_time()
        else:
            output("Initial WiFi connection failed.")
    except Exception as e:
        output("Initial WiFi setup error:", str(e))

    # Start key tasks regardless of WiFi connection state
    #asyncio.create_task(monitor_valves())
    asyncio.create_task(send_data())
    asyncio.create_task(maintain_wifi_connection())

    uart0.write(b'\r\npico-w> ')
    while True:
        hb.toggle()  # Heartbeat LED toggle
        await asyncio.sleep(1)

# Start the event loop
asyncio.run(main())
