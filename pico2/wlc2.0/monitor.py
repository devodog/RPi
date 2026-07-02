import uasyncio as asyncio
from helpers import *
import state


async def monitor_valves():
    # Must also monitor the water level in each reservoir, which is to be reported the web site's backend.
    global state
    while True:
        output("Monitoring valves and water levels every 60 seconds...")
        hour = hour_of_day()
        # The irrigation system is set to turn on every morning at 8:00 AM, 
        # and will run for 20 minutes. After that, it will close the valves to avoid flooding.
        if hour == 8:
            if valve_sw.value() == CLOSED:
                turn_on_SW_valve()
                state.valve_sw_opened = get_epoch_timestamp(2)
            if valve_ne.value() == CLOSED:
                turn_on_NE_valve()
                state.valve_ne_opened = get_epoch_timestamp(2)
            # For safety, if the valves are still open after 20 minutes, close them to avoid flooding.
            if hour == 8 and minute_of_hour() > 20:
                if valve_sw.value() == OPEN:
                    close_southwest_valve(None)
                if valve_ne.value() == OPEN:
                    close_northeast_valve(None)

        water_level_sw = 25 
        water_level_ne = 25 
        # We'll lock the water level to 25% for now, as we don't use this 
        # information since the irrigation system will turn on every morning at 8.
        
        valve_sw_status = valve_sw.value()
        valve_ne_status = valve_ne.value()

        # Resevoirs southwest - if one of the reservoirs is empty, open the valve to fill all.
        
        # The above comment is outdated. Sensores used are producing copper-
        # sulfate in the water, which si considewred to be slightly toxic. 
        # Therefore, these sensors are removed, and the water level is locked
        # to 25% - to please the monitoring system... the reste of the code
        # is kept for future use, in case we want to add the sensors back.

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
        elif water_level_sw == 0:
            output("Southwest reservoir is dry, and SW Valve is: ", valve_sw_status and "OPEN" or "CLOSED")
        
        if water_level_ne == 100:
            output("NorthEast reservoir is wet, and NE Valve is: ", valve_ne_status and "OPEN" or "CLOSED")
        elif water_level_ne == 0:
            output("NorthEast reservoir is dry, and NE Valve is: ", valve_ne_status and "OPEN" or "CLOSED")

        # 15 minutes
        await asyncio.sleep(60)
