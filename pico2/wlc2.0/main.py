
from wifi import *
from monitor import monitor_valves
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
    "    |__________________|\r\n"
    "      |  ||      ||  |\r\n"
    "      |  ||      ||  |\r\n"
    "      '--------------'\r\n"
)
output("START\r\n")
cmd_output(ascii_art, "")
cmd_output("wlc version: " + get_WLC_Version() + "\r\n", "")
async def main():
    global valve_ne, valve_sw
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
    asyncio.create_task(monitor_valves())
    asyncio.create_task(send_data())
    asyncio.create_task(maintain_wifi_connection())

    uart0.write(b'\r\npico-w> ')
    while True:
        hb.toggle()  # Heartbeat LED toggle
        # Read pin 2 and pin 6 to check if the valves are open and if the water level is full, then close the valves if necessary.
        if Pin(2).value() == 0 and valve_sw.value() == OPEN:
            close_southwest_valve(None)
            output("Southwest reservoir full! Closing South-West valve.")
        if Pin(6).value() == 0 and valve_ne.value() == OPEN:
            close_northeast_valve(None)
            output("Northeast reservoir full! Closing North-East valve.")        
        time.sleep(0.5)  # 0.5 second delay for heartbeat and valve checks
        await asyncio.sleep(1)

# Start the event loop
asyncio.run(main())
