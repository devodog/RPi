import uasyncio as asyncio
from helpers import *
import state
import gc
import requests


async def monitor_valves():
    # Must also monitor the water level in each reservoir, which is to be reported the web site's backend.
    while True:
        
        # Resevoir southwest
        if valve_sw.value() == CLOSED and (read_waterLevel(SouthWest) == 25 or read_waterLevel(SouthWest) == 0):
            turn_on_valve(valve_sw)
            state.valve_sw_opened = get_epoch_timestamp(2)

        # Resevoir northeast
        if valve_ne.value() == CLOSED and (read_waterLevel(NorthEast) == 25 or read_waterLevel(NorthEast) == 0):
            turn_on_valve(valve_ne)
            state.valve_ne_opened = get_epoch_timestamp(2)

       
        # A POST request to the API
        if wifi.wlan.isconnected():
            try:
                gc.collect()
                output("Sending post request to: ", read_config()["url"])
                json_data = build_json_data()
                response = requests.post(read_config()["url"], json=json_data, timeout=5)  # set timeout to avoid hanging
                
                output("Status code: ", str(response.status_code))
            except Exception as e:
                output("Error sending POST request: ", str(e))


       

        await asyncio.sleep(30)
