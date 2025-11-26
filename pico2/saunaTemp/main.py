## -*- coding: utf-8 -*-
from wifi import *
from helpers import *
from command_handler import read
from machine import Pin
import time


# LED Hart beat...
hb = Pin("LED", Pin.OUT)

# Set up UART interrupt
Pin(1).irq(read, trigger=Pin.IRQ_FALLING)

# Show the temperature value on a LCD display.

ascii_art = (
    "     .----------------.\r\n"
    "    |   Raspberry Pi   |\r\n"
    "    |      Pico W      |\r\n"
    "    |  .------------.  |\r\n"
    "    |  | [] [] [] []|  |\r\n"
    "    |  | [] [] [] []|  |\r\n"
    "    |  '------------'  |\r\n"
    "    |__________________|\r\n"
    "      |  ||      ||  |\r\n"
    "      |  ||      ||  |\r\n"
    "      '--------------'\r\n"
)
output("START\r\n")
cmd_output(ascii_art, "")

async def main():
    # Attempt initial connection (non-blocking success not critical)
    # One attempt only...for now
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

    # start background polling task
    asyncio.create_task(read_temp())
    
    uart0.write(b'\r\npico-w> ')
    while True:
        hb.toggle()
        await asyncio.sleep(1)

# Start the event loop
asyncio.run(main())
