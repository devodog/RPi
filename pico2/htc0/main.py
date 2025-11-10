## -*- coding: utf-8 -*-
from wifi import *
from helpers import *
from command_handler import read
from machine import Pin
import time

'''
The htc0 project is to make a generic and simple humidity and temperature 
monitor that can also use its information to activate a heater if the 
measured temperature is below a specified value, or turn om a dehumidifier
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
output("START of Humidity & Temperature measurements.\r\n")
cmd_output(ascii_art, "")

async def main():
    '''
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
    '''
    uart0.write(b'\r\npico-w>\r\n')
    # start background polling task
    asyncio.create_task(read_temp())
    
    
    while True:
        hb.toggle
        await asyncio.sleep(1)

# Start the event loop
asyncio.run(main())
