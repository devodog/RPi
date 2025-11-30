from machine import UART, Pin, I2C, reset
import uasyncio as asyncio
import time
import ntptime
from collections import OrderedDict
import wifi
import requests
import json
from machine import ADC
from lcd_display import LCD
from am2320 import AM2320   #AOSONG AM2320 sensor driver


uart0 = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))


SWITCH_OFF = 0
SWITCH_ON = 1

dehumidifierSwitch = Pin(16, Pin.OUT)
heaterSwitch = Pin(17, Pin.OUT)

dehumidifierState = SWITCH_OFF
heaterState = SWITCH_OFF

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

# Initialize LCD
lcd = LCD()

# Initialize I2C and sensor
#i2c = I2C(1, scl=Pin(3), sda=Pin(2))  # Adjust pins as needed
i2c = I2C(1, scl=Pin(27), sda=Pin(26))  # Adjust pins as needed
am2320_sensor = AM2320(i2c)

humidityHighThreshold = read_config()['highHumidityThreshold']
lowThreshold = read_config()['okHumidityOffset']

temperatureLowThreshold = read_config()['lowTempThreshold']
highThreshold = read_config()['okHumidityOffset']

humidityControlEnabled = read_config()['humidityControlEnabled']
temperatureControlEnable = read_config()['temperatureControlEnable']

# here we need a function to check whether the humidity and / or temperature is
# above or under a specific value - high to low threshold for activation or 
# release. 

# If the temperature is lower or equal to the Minimum temperature threshold, the heater switch will be activated, if enabled.
# When the temperature is 3 to 5 degrees Centigrade over the Minimum temperature threshold, the heater switch will be deactivated.

# If the humidity is over or equal to the Maximum humidity threshold, dehumidifier switch will activated, if enabled.
# When the humidity is 10 to 20 % lower than the Maximum humidity threshold, the dehumidifier switch will be deactivated.

async def read_am2320():
    global heaterState
    global dehumidifierState

    while True:
        try:
            humidity, temp = am2320_sensor.read()            
            if temp is not None and humidity is not None:
                output("AM2320.: ", f"{temp:.1f}°C")
                output("AM2320.: ", f"{humidity:.1f} %")
                lcd.clear()
                lcd.set_cursor(0,0)
                lcd.write_string("AM2320: " f"{temp:.1f}ßC")
                lcd.write_string("\nAM2320: " f"{humidity:.1f} %")
            
                if temperatureControlEnable is True:
                    if  temp <= temperatureLowThreshold:
                        heaterSwitch.value(SWITCH_ON)
                        heaterState = SWITCH_ON
                    elif temp >= (temperatureLowThreshold + highThreshold):
                        heaterSwitch.value(SWITCH_OFF)
                        heaterState = SWITCH_OFF

                if humidityControlEnabled is True:
                    if  humidity >= humidityHighThreshold:
                        dehumidifierSwitch.value(SWITCH_ON)
                        dehumidifierState = SWITCH_ON
                    elif humidity <= (humidityHighThreshold - lowThreshold):
                        dehumidifierSwitch.value(SWITCH_OFF)
                        dehumidifierState = SWITCH_OFF
            
                '''
                if wifi.wlan.isconnected():
                    try:
                        current_json_data = build_json_data()
                        output("Sending post request to: ", read_config()["url"])
                        response = requests.post(read_config()["url"], json=current_json_data, timeout=5)
                        output("Status code: ", str(response.status_code))
                    except Exception as e:
                        output("Error sending POST request: ", str(e))
                '''
        except Exception as e:
            cmd_output("AM2320 read error: ", str(e))

        await asyncio.sleep(60)

def power_switch_ctrl():
    if wifi.wlan.isconnected():
        try:
            get_respons = requests.get("https://midtskips.no/garasje/api/env/state.txt")
            output("Status code: ", str(get_respons.status_code))
        except Exception as e:
            output("Error sending POST request: ", str(e))
        # is there an operation for execute?

def build_json_data():
    humidity, temperature = am2320_sensor.read()
    return {
        "Time": time.time(),
        "Temperature": temperature,
        "Humidity": humidity
   }
