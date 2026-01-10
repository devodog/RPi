## -*- coding: utf-8 -*-
from wifi import *
from helpers import *
from command_handler import read
from machine import Pin
import time

'''
The htControl MicroPython project is to make a generic and simple humidity and
temperature monitor that can also use its information to activate a heater if
the measured temperature is below a specified value, or turn om a dehumidifier
when the indoor environment is too moist.

The sensor used is a AOSONG AM2320 configured for i2c communication.
'''
# LED Hart beat...
hb = Pin("LED", Pin.OUT)

# Set up UART interrupt
Pin(1).irq(read, trigger=Pin.IRQ_FALLING)


# Read the ADC connected to the LM35 for measuring the temperature.
# -- this device is not necessarily optimal for the intended use.
#
# Show the temperature value on a LCD display.

ascii_art = (
    "     .----------------.\r\n"
    "    |   Raspberry Pi   |\r\n"
    "    |     Pico 2 W     |\r\n"
    "    |  .------------.  |\r\n"
    "    |  | [] [] [] []|  |\r\n"
    "    |  | [] [] [] []|  |\r\n"
    "    |  '------------'  |\r\n"
    "    |__________________|\r\n"
    "      |  ||      ||  |\r\n"
    "      |  ||      ||  |\r\n"
    "      '--------------'\r\n"
    "  Humidity and Temperature\r\n"
    "    monitor and control\r\n"
)
output("START ver.1.02 as of 8JAN26")
cmd_output(ascii_art, "")

monitorState("no") # no change...

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
    
    output("Initializing environment control")
    initControl()

    uart0.write(b'\r\npico-w>\r\n')
    # start background polling tasks
    asyncio.create_task(maintain_wifi_connection())
    asyncio.create_task(indoorClimateControl())
    
    slowHB = 0
    while True:
        if wlan.isconnected():
            hb.toggle()
        else:
            slowHB += 1
            if slowHB > 3:
                hb.toggle()
                slowHB = 0
        await asyncio.sleep(1)
# Start the event loop
asyncio.run(main())
