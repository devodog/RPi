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
    "      |  | BADSTU |  |\r\n"
    "      '--------------'\r\n"
)
output("START ver. 1.01 as of 15MAR26\r\n")
cmd_output(ascii_art, "")

async def main():
    infoOnLCD("Badstutemp v1.01\nPlease wait.")
    time.sleep(2)  
    # Attempt initial connection (non-blocking success not critical)
    try:
        cmd_output(f"Attempting to connect to WiFi AP:")
        cmd_output(f"SSID....: {read_config()['wifi']['SSID']}")

        infoOnLCD(f"Connecting to\n{read_config()['wifi']['SSID']}")
        cmd_output(f"PASSWORD: {read_config()['wifi']['PASSWORD']}")
        connect_wifi(read_config())    
        await asyncio.sleep(4)  # Use async sleep for non-blocking
        if wlan.isconnected():
            output("WiFi connected!")
            output("IP Address: ", wlan.ifconfig()[0])
            sync_time()
        else:
            output("Initial WiFi connection failed.")
            infoOnLCD("Unable to con-\nnect to WiFi.")
    except Exception as e:
        output("Initial WiFi setup error:", str(e))
    

    uart0.write(b'\r\npico-w> ')

    # start background polling task
    asyncio.create_task(maintain_wifi_connection())
    asyncio.create_task(read_temp())
    
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