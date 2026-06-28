from machine import UART, Pin, reset, I2C
#from scd30 import SCD30
import uasyncio as asyncio
import time
import ntptime
from collections import OrderedDict
import state
import wifi
import json
from dht import DHT11


OPEN = 1
CLOSED = 0

SouthWest = 0
NorthEast = 1

# gp2 - gp5 register water level in the SW (South-West water reservoir), while 
# gp6 - gp9 register water level in the NE (North-East water reservoir)

# South west sensor
gp2 = Pin(2, Pin.IN)
gp3 = Pin(3, Pin.IN)
gp4 = Pin(4, Pin.IN)
gp5 = Pin(5, Pin.OUT)


# North east sensor
gp6 = Pin(6, Pin.IN)
gp7 = Pin(7, Pin.IN)
gp8 = Pin(8, Pin.IN)
gp9 = Pin(9, Pin.OUT)


# Water valve 1
valve_sw = Pin(16, Pin.OUT)

# Water valve 2
valve_ne = Pin(17, Pin.OUT)


uart0 = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
sensor = DHT11(Pin(26))  # DHT11 sensor on GPIO26 (adjust as needed)

#global sensor_connected
sensor_connected = False

def output(text, arg="", delay=0.1):
    
    local_time = get_local_timestamp(2)
    uart0.write(b'[' + local_time.encode() + b'] ' + text.encode() + arg.encode() + b'\r\n')
    time.sleep(delay)


def cmd_output(text, arg="", delay=0.1):
    uart0.write(text.encode() + arg.encode() + b'\r\n')
    time.sleep(delay)

def read_config():
    with open("config.json", "r") as f:
        config = json.load(f)
        return config
    
def change_config(buf):
    config = read_config()
    try:
        if "ssid" in buf or "password" in buf:
            cmd_output(f"Old {buf.split('=')[0].upper()}: ", config["wifi"][buf.split('=')[0].upper()])
            config["wifi"][buf.split("=")[0].upper()] = buf.split("=")[1]
        elif "url" in buf:
            cmd_output(f"Old {buf.split('=')[0]}: ", config[buf.split('=')[0]])
            config[buf.split('=')[0]] = buf.split("=")[1]
        elif "attempts" in buf or "freq" in buf:
            cmd_output(f"Old {buf.split('=')[0]}: ", config["wifi"][buf.split('=')[0]])
            try:
                config["wifi"][buf.split("=")[0]] = int(buf.split("=")[1])
            except ValueError:
                cmd_output("Invalid value: Must be an integer.")
                
        # Write updated config
        with open("config.json", "w") as f:
            json.dump(config, f)

        cmd_output("Updated config: ")
        print_config()
    except KeyError:
        cmd_output(f"[-]ERROR: {buf.split('=')[0]} not in config.json")
    

def print_info():
    cmd_output("\n=== WiFi Connection ===")
    ip = wifi.wlan.ifconfig()[0] if wifi.wlan.isconnected() else 'not connected'
    cmd_output(f"Pico IP Address:{'':<12} {ip}")

    # Get fresh sensor and valve data from build_json_data
    data = build_json_data()

    cmd_output("\n=== SENSORS ===")
    # Print top-level sensor values explicitly
    cmd_output(f"{'Temperature':<12}: {data['Temperature']}")
    cmd_output(f"{'Humidity':<12}: {data['Humidity']}")
    cmd_output(f"{'CO2':<12}: {data['CO2']}")
    
    cmd_output("\n=== WATERLEVEL ===")
    # data['Waterlevel'] is a list with one dict inside
    for location, level in data["Waterlevel"][0].items():
        cmd_output(f"{location:<12}: {level}")

    cmd_output("\n=== VALVES ===")
    # data['Valves'] is a list with one dict inside, valves info is nested
    for valve_name, valve_info in data["Valves"][0].items():
        cmd_output(valve_name)
        for key, val in valve_info.items():
            cmd_output(f"  {key:<25}: {val}")
    cmd_output("")


def print_config():
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
    except Exception as e:
        cmd_output("Failed to load config.json:", str(e))
        return

    cmd_output("\n=== CONFIGURATION ===")
    cmd_output(f"Version: \t{config.get('version', '-')}")
    
    wifi = config.get("wifi", {})
    cmd_output("WiFi SSID: \t", wifi.get("SSID", "-"))
    cmd_output("WiFi PASS: \t", wifi.get("PASSWORD", "-"))

    cmd_output("Post URL: \t", config.get("url", "-"))
    cmd_output("")

def print_help():
    help_text = (
    "\nHelp menu:\r\n"
    "-------------------------\r\n"
    "info               \tShows info about the system\r\n"
    "config             \tShows contents of config.json\r\n"
    "url=<url>          \tChanges URL in config.json to <url>\r\n"
    "ssid=<ssid>        \tChanges SSID in config.json to <ssid>\r\n"
    "password=<pwd>     \tChanges PASSWORD in config.json to <pwd>\r\n"
    "attempts=<int>     \tNumber of WiFi reconnection attempts (default: 10)\r\n"
    "freq=<int>         \tSleep interval between each bulk of reconnection attempts (default: 10min)\r\n"
    "restart            \tRestarts the pico\r\n"
    "version            \tShows current version"
)
    cmd_output(help_text)
    cmd_output("")

def turn_on_valve(valve):
    output("Turning on valve: ", valve)
    valve.value(1)

def turn_off_valve(valve):
    output("Turning off valve: ", valve)
    valve.value(0)

def close_southwest_valve(pin):
    if valve_sw.value() == OPEN and read_waterLevel(SouthWest) == 100:
        output("Closing SouthWest valve")
        turn_off_valve(valve_sw)
        state.valve_sw_closed = get_epoch_timestamp(2)
        output("closed: ", str(state.valve_sw_closed))
        state.valve_sw_duration = timestamp_diff(state.valve_sw_opened, state.valve_sw_closed)
        output("duration: ", str(state.valve_sw_duration))

def close_northeast_valve(pin):
    if valve_ne.value() == OPEN and read_waterLevel(NorthEast) == 100:
        output("Closing NorthEast valve")
        turn_off_valve(valve_ne)
        state.valve_ne_closed = get_epoch_timestamp(2)
        state.valve_ne_duration = timestamp_diff(state.valve_ne_opened, state.valve_ne_closed)

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

def get_epoch_timestamp(offset_hours=0):
    """Return current time as integer epoch timestamp, optionally with offset."""
    return int(time.time() + offset_hours * 3600)

def timestamp_diff(t1_epoch, t2_epoch):
    """Return difference in seconds between two epoch timestamps."""
    return abs(int(t2_epoch) - int(t1_epoch))


# There are now three reservoirs, each either full or empty.
def read_waterLevel(reservoir):
    '''
    For the SouthWest reservoirs:
    The water level detection is differentiated - two reservoirs will detect 
    when they are empty as the sensor will indicate a high signal.
    These two will be connected to GPIO3 and GPIO4.
    GPIO2 will be used for detecting when the first reservoir is full, issuing
    an interrupt to close the valve.

    For the NorthEast reservoirs:
    The same applies as for the SouthWest reservoirs, but with GPIO6, GPIO7, 
    and GPIO8, where GPIO7 and GPIO8 will detect when the reservoirs are empty, 
    and GPIO6 will detect when the first reservoir is full, 
    issuing an interrupt to close the valve.
    '''
    if reservoir == SouthWest:
        # Turn on the output pin for the SouthWest reservoirs
        gp5.value(1)
        if gp3.value() == 0 or gp4.value() == 0:
            gp5.value(0)  # Turn off the output pin after reading
            return 100
        else:
            gp5.value(0)  # Turn off the output pin after reading
            return 0        
    elif reservoir == NorthEast:
        # Turn on the output pin for the NorthEast reservoirs
        gp6.value(1)
        if gp7.value() == 0 or gp8.value() == 0:
            gp6.value(0)  # Turn off the output pin after reading
            return 100
        else:
            gp6.value(0)  # Turn off the output pin after reading
            return 0
    
def read_DHT11():
    global sensor, sensor_connected
    """
    Read temperature and humidity from DHT11 sensor.
    Returns: (temperature_celsius, humidity_percent)
    """
    try:
        # Initialize DHT11 on GPIO pin (adjust pin number as needed)
        sensor.measure()
        temperature = sensor.temperature()
        humidity = sensor.humidity()
        output(f"DHT11 - Temp: {temperature} °C, Humidity: {humidity} %")
        sensor_connected = True  # Mark sensor as connected if reading is successful
        output("DHT11sensor_connected: ", sensor_connected and "Yes" or "No")
        return (temperature, humidity)
    except Exception as e:
        output("Error reading DHT11:", str(e))
        sensor_connected = False
        output("DHT11sensor_connected: ", sensor_connected and "Yes" or "No")

        return (0, 0)
    
def getSensorConnectedStatus():
    global sensor_connected
    output("getSensorConnectedStatus: ", sensor_connected and "Yes" or "No")
    return sensor_connected

def build_json_data():
    temperature, humidity = read_DHT11()
    return {
        "Temperature": round(temperature, 1),
        "Humidity": round(humidity, 1),
        "Waterlevel": [
            {
                "SouthWest": read_waterLevel(SouthWest),
                "NorthEast": read_waterLevel(NorthEast)
            }
        ],
        "Valves": [
            {
                "SouthWest": {
                    "Status": check_valve(valve_sw.value()),
                    "Last opened": state.valve_sw_opened,
                    "Last closed": state.valve_sw_closed,
                    "Duration valve was open": state.valve_sw_duration
                },
                "NorthEast": {
                    "Status": check_valve(valve_ne.value()),
                    "Last opened": state.valve_ne_opened,
                    "Last closed": state.valve_ne_closed,
                    "Duration valve was open": state.valve_ne_duration
                }
            }
        ]
    }
