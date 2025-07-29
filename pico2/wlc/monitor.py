import uasyncio as asyncio
from helpers import *
import state


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

        # 15 minutes
        await asyncio.sleep(60)
