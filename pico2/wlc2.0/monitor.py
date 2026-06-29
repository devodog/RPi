import uasyncio as asyncio
from helpers import *
import state


async def monitor_valves():
    # Must also monitor the water level in each reservoir, which is to be reported the web site's backend.
    
    while True:
        
        # Resevoirs southwest - if one of the reservoirs is empty, open the valve to fill all.
        if valve_sw.value() == CLOSED and (read_waterLevel(SouthWest) == 0):
            turn_on_SW_valve()
            state.valve_sw_opened = get_epoch_timestamp(2)

        # Resevoirs northeast
        if valve_ne.value() == CLOSED and (read_waterLevel(NorthEast) == 0):
            turn_on_NE_valve()
            state.valve_ne_opened = get_epoch_timestamp(2)

        # 15 minutes
        await asyncio.sleep(60)
