from machine import UART, Pin, reset
import sys
import time
import ntptime
from collections import OrderedDict
import state
import wifi
import json

EMPTY = 1
FULL = 0

SouthWest = 0
NorthEast = 1

# gp2 - gp5 register water level in the SW (South-West water reservoir), while 
# gp6 - gp9 register water level in the NE (North-East water reservoir)

# Sensor 1
gp2 = Pin(2, Pin.IN)
gp3 = Pin(3, Pin.IN)
gp4 = Pin(4, Pin.IN)
gp5 = Pin(5, Pin.IN)

# Sensor 2
gp6 = Pin(6, Pin.IN)
gp7 = Pin(7, Pin.IN)
gp8 = Pin(8, Pin.IN)
gp9 = Pin(9, Pin.IN)



# Water valve 1
valve_a = Pin(16, Pin.OUT)

# Water valve 2
valve_b = Pin(17, Pin.OUT)

# State flags
# valve_a_open = False
# valve_b_open = False

# The API endpoint
url = "http://midtskips.no/drivhus/rx_data.php"



uart0 = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))


def output(text, arg=""):
    
    local_time = get_local_timestamp(2)
    uart0.write(b'[' + local_time.encode() + b'] ' + text.encode() + arg.encode() + b'\r\n')

def cmd_output(text, arg=""):
    uart0.write(text.encode() + arg.encode() + b'\r\n')

def read_config():
    with open("config.json", "r") as f:
        config = json.load(f)
        return config
    
def turn_on_valve(valve):
    valve.value(1)

def turn_off_valve(valve):
    valve.value(0)

def check_valve(valve):
    if valve == True:
        return "open"
    else:
        return "closed"

def sync_time():
    # Sync with NTP server (sets RTC to UTC)
    ntptime.settime()
    # Get current local time (in UTC)
    t = time.localtime()
    output("NTP TIME: ", get_local_timestamp(2))
    
def get_local_timestamp(offset_hours=0):
    t = time.localtime(time.time() + offset_hours * 3600)
    return f"{t[0]:04}-{t[1]:02}-{t[2]:02} {t[3]:02}:{t[4]:02}:{t[5]:02}"

def parse_timestamp(ts_str):
    # Example input: "2025-07-13 15:20:55"
    date_part, time_part = ts_str.split(" ")
    year, month, day = map(int, date_part.split("-"))
    hour, minute, second = map(int, time_part.split(":"))
    return (year, month, day, hour, minute, second, 0, 0)

def timestamp_diff(t1_str, t2_str):
    t1_tuple = parse_timestamp(t1_str)
    t2_tuple = parse_timestamp(t2_str)
    t1_epoch = time.mktime(t1_tuple)
    t2_epoch = time.mktime(t2_tuple)
    diff = abs(t2_epoch - t1_epoch)
    minutes = int(diff // 60)
    seconds = int(diff % 60)
    return f"{minutes}min, {seconds}sec"

def read_waterLevel(reservoir):
    if reservoir == SouthWest:
        if gp2.value() == 0:
            return "Full"
        elif gp3.value() == 0:
            return "3/4 Full"
        elif gp4.value() == 0:
            return "1/2 Full"
        elif gp5.value() == 0:
            return "1/4 Full"
        else:
            return "Empty"        
    elif reservoir == NorthEast:
        if gp6.value() == 0:
            return "Full"
        elif gp7.value() == 0:
            return "3/4 Full"
        elif gp8.value() == 0:
            return "1/2 Full"
        elif gp9.value() == 0:
            return "1/4 Full"
        else:
            return "Empty"
    
def fun(a):
    if isinstance(a, OrderedDict):
        d = {}
        for k, v in a.items():
            d[k] = fun(v) if isinstance(v, OrderedDict) else v
        return d
    return a


json_data = OrderedDict([
        ("Sensors", [
            OrderedDict([
                ("SouthWest", read_waterLevel(SouthWest)),
                ("NorthEast", read_waterLevel(NorthEast))
            ])
        ]),
        ("Valves", [
            OrderedDict([
                ("SouthWest", OrderedDict([
                    ("Status", check_valve(state.valve_a_open)),
                    ("Last opened", state.valve_a_opened),
                    ("Last closed", state.valve_a_closed),
                    ("Duration valve was open", state.valve_a_duration)
                ])),
                ("NorthEast", OrderedDict([
                    ("Status", check_valve(state.valve_b_open)),
                    ("Last opened", state.valve_b_opened),
                    ("Last closed", state.valve_b_closed),
                    ("Duration valve was open", state.valve_b_duration)
                ]))
            ])
        ])
    ])