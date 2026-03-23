## -*- coding: utf-8 -*-

from helpers import *
from command_handler import read
from machine import Pin
import time
import micropython

# Config
PIN_NUM = 15                 # GP 15 = input pin for event sensor
BELT_LENGTH_M = 3.1          # belt length in meters (per full rotation/one event)
TRIGGER_RISING = True        # True for rising-edge, False for falling-edge

# Shared state (kept minimal for ISR)
micropython.alloc_emergency_exception_buf(100)
_ts_last = 0         # last timestamp in microseconds
_has_new = False     # flag set in ISR when new interval ready
_interval_us = 0     # computed interval in microseconds

# IRQ handler: record timestamp and compute interval
def _irq_handler(pin):
    global _ts_last, _has_new, _interval_us
    t = time.ticks_us()
    if _ts_last == 0:
        _ts_last = t
        return
    # compute difference safely (handles wrap)
    dt = time.ticks_diff(t, _ts_last)   # signed int in µs
    _ts_last = t
    _interval_us = dt if dt >= 0 else -dt
    _has_new = True

# Setup pin and attach IRQ
p = Pin(PIN_NUM, Pin.IN, Pin.PULL_DOWN)
trigger = Pin.IRQ_RISING if TRIGGER_RISING else Pin.IRQ_FALLING
p.irq(trigger=trigger, handler=_irq_handler)

# Helper: convert interval (µs) to km/h
def interval_us_to_kmh(interval_us, belt_length_m):
    # interval_us is microseconds per event (one full belt length)
    # speed_m_s = belt_length_m / (interval_us / 1_000_000)
    # speed_km_h = speed_m_s * 3.6
    if interval_us <= 0:
        return 0.0
    speed_m_s = belt_length_m * 1_000_000.0 / interval_us
    return speed_m_s * 3.6

# LED Hart beat...
hb = Pin("LED", Pin.OUT)

# Set up UART interrupt
Pin(1).irq(read, trigger=Pin.IRQ_FALLING)


# Show the tred mill speed on a LCD display.

ascii_art = (
    "     .----------------.\r\n"
    "    |   Raspberry Pi   |\r\n"
    "    |      Pico 2      |\r\n"
    "    |  .------------.  |\r\n"
    "    |  | [] [] [] []|  |\r\n"
    "    |  | [] [] [] []|  |\r\n"
    "    |  '------------'  |\r\n"
    "    |__________________|\r\n"
    "      |  ||      ||  |\r\n"
    "      |  |        |  |\r\n"
    "      '--------------'\r\n"
)
output("START ver. 0.00 as of 10JAN26\r\n")
cmd_output(ascii_art, "")

def main():
    global _has_new, _interval_us
    print("Belt speed monitor starting (pin {}, belt {:.3f} m)".format(PIN_NUM, BELT_LENGTH_M))
    uart0.write(b'\r\npico-2> ')
    while True:
        if _has_new:
            # briefly disable IRQ while copying shared vars to avoid races
            p.irq(handler=None)
            interval = _interval_us
            _has_new = False
            p.irq(trigger=trigger, handler=_irq_handler)

            # compute and display
            kmh = interval_us_to_kmh(interval, BELT_LENGTH_M)
            # interval in seconds with ms precision
            interval_s = interval / 1_000_000.0
            print("Interval: {:.3f} s  Speed: {:.2f} km/h".format(interval_s, kmh))
        time.sleep_ms(50)

if __name__ == "__main__":
    main()
