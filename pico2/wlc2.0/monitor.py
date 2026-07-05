import uasyncio as asyncio
from helpers import *
import state


async def monitor_valves():
    # Must also monitor the water level in each reservoir, which is to be reported the web site's backend.
    global state
    start_irrigation = 12
    end_irrigation = 22
    duration = 10
    output("Starting monitor_valves task...")
    while True:
        output("Periodic Irrigation check at: " + hour_of_day() + ":" + minute_of_hour())
        hour = int(hour_of_day())
        minuteOfTheHour = int(minute_of_hour())
        # The irrigation system is set to turn on every morning at 8:00 AM, 
        # and will run for 20 minutes. After that, it will close the valves to avoid flooding.
        if hour == start_irrigation and minuteOfTheHour >= end_irrigation and minuteOfTheHour < (end_irrigation + duration):
            output("Irrigation interval active...")
            if valve_sw.value() == CLOSED and Pin(2).value() == 1:
                turn_on_SW_valve()
                state.valve_sw_opened = get_epoch_timestamp(0)
            
            if valve_ne.value() == CLOSED and Pin(6).value() == 1:
                turn_on_NE_valve()
                state.valve_ne_opened = get_epoch_timestamp(0)
        
        # For safety, if the valves are still open after x minutes, close them to avoid flooding.
        if hour == start_irrigation and minuteOfTheHour > (end_irrigation + duration):
            output("Irrigation interval ended.")
            if valve_sw.value() == OPEN:
                close_southwest_valve(None)
            if valve_ne.value() == OPEN:
                close_northeast_valve(None)


        # 15 minutes
        await asyncio.sleep(60)
