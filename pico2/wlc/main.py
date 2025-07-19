import uasyncio as asyncio
import wifi
from monitor import monitor_valves
from webserver import start_server
from helpers import sync_time, output, uart0, read_config
from command_handler import read
from machine import Pin
import time
import json

# LED Hart beat..
hb = Pin("LED", Pin.OUT)

# Set up UART interrupt
Pin(1).irq(read, trigger=Pin.IRQ_FALLING)

async def main():
    while True:  # Infinite loop to keep trying
        

        output(f"Attempting to connect to WiFi using the following config:\r\nSSID: {read_config()['wifi']['SSID']}, PASSWORD: {read_config()['wifi']['PASSWORD']}")
        try:
            hb.toggle()
            wifi.connect_wifi(read_config())
            time.sleep(2)
            if wifi.wlan.isconnected():
                break  # Exit the loop if connected
        except Exception as e:
            output(f"Error: {e}")

        output("WiFi connection failed. Retrying...")
        time.sleep(5)  # Wait before retrying
    hb.toggle()
    output("WiFi connected!")
    output("IP Address: ", wifi.wlan.ifconfig()[0])
    
    
    asyncio.create_task(monitor_valves())
    uart0.write(b'\r\npico-w> ')
    await start_server()

# Start the event loop
asyncio.run(main())
