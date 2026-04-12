from machine import UART, Pin, reset, I2C, ADC
import uasyncio as asyncio
import time
import ntptime
from collections import OrderedDict
import state
import wifi
import json


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
gp5 = Pin(5, Pin.IN)


# North east sensor
gp6 = Pin(6, Pin.IN)
gp7 = Pin(7, Pin.IN)
gp8 = Pin(8, Pin.IN)
gp9 = Pin(9, Pin.IN)


# Water valve 1
valve_sw = Pin(16, Pin.OUT)

# Water valve 2
valve_ne = Pin(17, Pin.OUT)


uart0 = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))

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

    cmd_output("\n=== Sensor Data ===")
    cmd_output(f"Temperature: {'':<10} {data['Temperature']} °C")

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
    "version            \tShows current version")
    cmd_output(help_text)
    cmd_output("")


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

def read_LM35():
    """
    Read temperature from LM35 sensor via ADC2 (GPIO28).
    LM35 output: 10mV per degree Celsius
    Returns: (raw_adc_value, temperature_celsius)
    """
    adc = ADC(28)  # ADC2 is GPIO28
    
    # Read raw ADC value (0-65535 for 16-bit, or 0-4095 for 12-bit depending on config)
    raw_value = adc.read_u16()  # Returns 16-bit value (0-65535)
    
    # Convert to voltage: Pico ADC is 3.3V reference
    voltage = (raw_value / 65535) * 3.3
    
    # LM35: 10mV per °C, so 0.01V per °C
    temperature_celsius = voltage / 0.01
    
    return (raw_value, round(temperature_celsius, 1))
 
def build_json_data():
    return {
        "Temperature": round(read_LM35()[1], 1)
    }
