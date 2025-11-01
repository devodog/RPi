## -*- coding: utf-8 -*-
from helpers import *
from command_handler import read
from machine import Pin
import time


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
output("START\r\n")
cmd_output(ascii_art, "")

async def main():
    # start background polling task
    asyncio.create_task(poll_lm35())

    uart0.write(b'\r\npico-w> ')
    while True:
        await asyncio.sleep(1)

# Start the event loop
asyncio.run(main())
