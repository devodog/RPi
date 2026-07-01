import uasyncio as asyncio
from helpers import *
import state


async def monitor_valves():
    # Must also monitor the water level in each reservoir, which is to be reported the web site's backend.
    global state
    #loop_count = 0
    while True:
        ''' - - IGNORE ---
        hour = hour_of_day()
        if hour < 8 and hour > 11:
            loop_count += 1
            if (loop_count > 9): # If the loop has run for more than 10 iterations, reset it to avoid overflow.
                loop_count = 0
                output("Outside of the allowed time window for filling reservoirs. No action will be taken.")
            continue  # Skip the rest of the loop and wait for the next iteration
        '''
        output("Monitoring valves and water levels every 60 seconds...")
        water_level_sw = read_waterLevel(SouthWest)
        water_level_ne = read_waterLevel(NorthEast)
        valve_sw_status = valve_sw.value()
        valve_ne_status = valve_ne.value()


        # Resevoirs southwest - if one of the reservoirs is empty, open the valve to fill all.
        if valve_sw_status == CLOSED and water_level_sw == 0:
            turn_on_SW_valve()
            state.valve_sw_opened = get_epoch_timestamp(2)

        # Resevoirs northeast
        if valve_ne_status == CLOSED and water_level_ne == 0:
            turn_on_NE_valve()
            state.valve_ne_opened = get_epoch_timestamp(2)
        
        # Additional readout from the monitor...
        if water_level_sw == 100:
            output("Southwest reservoir is wet, and SW Valve is: ", valve_sw_status and "OPEN" or "CLOSED")
        else:
            output("Southwest reservoir is dry, and SW Valve is: ", valve_sw_status and "OPEN" or "CLOSED")
        
        if water_level_ne == 100:
            output("NorthEast reservoir is wet, and NE Valve is: ", valve_ne_status and "OPEN" or "CLOSED")
        else:
            output("NorthEast reservoir is dry, and NE Valve is: ", valve_ne_status and "OPEN" or "CLOSED")

        # 15 minutes
        await asyncio.sleep(60)
