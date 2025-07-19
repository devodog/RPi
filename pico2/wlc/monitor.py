import uasyncio as asyncio
from helpers import *
import state
import select

async def monitor_valves():

    while True:
        POOL_A_bottom = gp4.value()
        POOL_A_top = gp2.value()
        POOL_B_bottom = gp8.value()
        POOL_B_top = gp6.value()


        # POOL A logic
        if not state.valve_a_open and POOL_A_bottom == EMPTY:
            state.valve_a_open = True
            turn_on_valve(valve_a)
            state.valve_a_opened = get_local_timestamp(2)

        elif state.valve_a_open and POOL_A_top == FULL:
            state.valve_a_open = False
            turn_off_valve(valve_a)
            state.valve_a_closed = get_local_timestamp(2)
            state.valve_a_duration = timestamp_diff(state.valve_a_opened, state.valve_a_closed)

        # POOL B logic
        if not state.valve_b_open and POOL_B_bottom == EMPTY:
            state.valve_b_open = True
            turn_on_valve(valve_b)
            state.valve_b_opened = get_local_timestamp(2)

        elif state.valve_b_open and POOL_B_top == FULL:
            state.valve_b_open = False
            turn_off_valve(valve_b)
            state.valve_b_closed = get_local_timestamp(2)
            state.valve_b_duration = timestamp_diff(state.valve_b_opened, state.valve_b_closed)
        
        await asyncio.sleep(30)
