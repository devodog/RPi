import gc
from machine import UART, Pin, I2C, ADC, reset
import uasyncio as asyncio
import time
import ntptime
from collections import OrderedDict
import wifi
import requests
import json
#from lcd_display import LCD
from am2320 import AM2320   #AOSONG AM2320 sensor driver

# Global variables & Hardware configuartion
uart0 = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1), txbuf=1024)
dehumidifierSwitch = Pin(16, Pin.OUT)
heaterSwitch = Pin(17, Pin.OUT)

SWITCH_OFF = 0
SWITCH_ON = 1

monitor = True
### Default humidity and temperature control parameters
postInterval = 3 # currently 3 min interval for publishing data to the web...

dehumidifierState = SWITCH_OFF
heaterState = SWITCH_OFF

humidityControl = "Disabled"
temperatureControl = "Disabled"

humidityHighThreshold = 70
humidityLowThreshold = 60

temperatureLowThreshold = 3
temperatureHighThreshold = 7
############################## END Default control parameters

def initControl():
    config = read_config()
    postInterval = config.get("postInterval")
    envctrl = config.get("envctrl", {})
    global humidityControl
    global temperatureControl
    
    global humidityHighThreshold
    global humidityLowThreshold
    global temperatureLowThreshold
    global temperatureHighThreshold

    humidityControl = envctrl.get("humidityCtrl", "-")
    temperatureControl = envctrl.get("tempCtrl", "-")
    
    humidityHighThreshold = envctrl.get("humidityHigh", "-")
    humidityLowThreshold = envctrl.get("humidityLow", "-")
    temperatureLowThreshold = envctrl.get("tempLow", "-")
    temperatureHighThreshold = envctrl.get("tempHigh", "-")

def monitorState(change):
    global monitor
    monstate = "ON"
    if change == "on":
        monitor = True
    elif change == "off":
        monitor = False

    if monitor == False:
        monstate = "OFF"
    
    cmd_output("Monitor State: ", monstate)

def output(text, arg="", delay=0.1):
    if monitor == True:
        local_time = get_local_timestamp(1)
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
            cmd_output(f"Old {buf.split('=')[0]}: ", str(config["wifi"][buf.split('=')[0]]))
            try:
                config["wifi"][buf.split("=")[0]] = int(buf.split("=")[1])
            except ValueError:
                cmd_output("Invalid value: Must be an integer.")
        
        elif "humidityHigh" in buf or "humidityLow" in buf or "tempHigh" in buf or "tempLow" in buf:
            cmd_output(f"Old {buf.split('=')[0]}: ", str(config["envctrl"][buf.split('=')[0]]))
            try:
                config["envctrl"][buf.split("=")[0]] = int(buf.split("=")[1])
            except ValueError:
                cmd_output("Invalid value: Must be an integer.")
        elif "humidityCtrl" in buf or "tempCtrl" in buf:
            cmd_output(f"Old {buf.split('=')[0]}: ", config["envctrl"][buf.split('=')[0]])
            config["envctrl"][buf.split('=')[0]] = buf.split("=")[1] 

        # Write updated config
        with open("config.json", "w") as f:
            json.dump(config, f)

        cmd_output("Updated config: ")
        print_config()
        initControl()

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
    
    env = config.get("envctrl", {})
    cmd_output("Humidity Control: \t", env.get("humidityCtrl", "-"))
    cmd_output("Temp Control: \t\t", env.get("tempCtrl", "-"))
    cmd_output("Humidity high threshold: \t", str(env.get("humidityHigh", "-")))
    cmd_output("Humidity low threshold: \t", str(env.get("humidityLow", "-")))
    cmd_output("Temp high threshold: \t", str(env.get("tempHigh", "-")))
    cmd_output("Temp low threshold: \t", str(env.get("tempLow", "-")))

    cmd_output("")

def print_help():
    help_text = (
    "\nHelp menu:\r\n"
    "-------------------------\r\n"
    "help               \tThis information\r\n"
    "info               \tShows info about the system\r\n"
    "config             \tShows contents of config.json\r\n"
    "url=<url>          \tChanges URL in config.json to <url>\r\n"
    "postInt=<int>      \tNumber of minutes between each POST\r\n"
    "ssid=<ssid>        \tChanges SSID in config.json to <ssid>\r\n"
    "password=<pwd>     \tChanges PASSWORD in config.json to <pwd>\r\n"
    "attempts=<int>     \tNumber of WiFi reconnection attempts (default: 10)\r\n"
    "freq=<int>         \tSleep interval between each bulk of reconnection attempts (default: 10min)\r\n"
    "restart            \tRestarts the pico\r\n"
    "version            \tShows current version\r\n"
    "humidityCtrl=<enabled|disabled>\r\n"
    "tempCtrl=<enabled|disabled>\r\n"
    "humidityHigh=<int> \tHigh humidity level threshold for switch ON\r\n"
    "humidityLow=<int>  \tLow humidity level threshold for switch OFF\r\n"
    "tempHigh=<int>     \tHigh temperature level threshold for heater OFF\r\n"
    "tempLow=<int>      \tLow temperature level threshold for heater ON\r\n"
    )
    cmd_output(help_text)
    cmd_output("")

def switchCtrl(sw, state):
    if (sw == 1):
        if (state == SWITCH_ON):
            dehumidifierSwitch.value(SWITCH_ON)
            dehumidifierState = SWITCH_ON
        else:
            dehumidifierSwitch.value(SWITCH_OFF)
            dehumidifierState = SWITCH_OFF
    else:
        if (state == SWITCH_ON):
            heaterSwitch.value(SWITCH_ON)
            heaterState = SWITCH_ON
        else:
            heaterSwitch.value(SWITCH_OFF)
            heaterState = SWITCH_OFF

def sync_time():
    # Sync with NTP server (sets RTC to UTC)
    ntptime.settime()
    # Get current local time (in UTC)
    t = time.localtime()
    output("NTP TIME: ", get_local_timestamp(1))
    
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

###############################################################################
# Initialize I2C and sensor
# GPIO 26 and GPIO 27 is made accessable on the LEDstripDrv2.0 PCB
# two screw terminales.
# terminal-pin 1 = GPIO 26 = i2c SDA
# terminal-pin 2 = GPIO 27 = i2c SCL
i2c = I2C(1, scl=Pin(27), sda=Pin(26))  
am2320_sensor = AM2320(i2c)

async def indoorClimateControl():
    global postInterval
    global heaterState
    global dehumidifierState

    global humidityControl
    global temperatureControl
    global humidityHighThreshold
    global humidityLowThreshold
    global temperatureLowThreshold
    global temperatureHighThreshold

    interval = 1

    while True:
        try:
            humidity, temp = am2320_sensor.read()            
            if temp is not None and humidity is not None:

                output("AM2320.: ", f"{temp:.1f}°C")
                output("AM2320.: ", f"{humidity:.1f} %")
                '''
                lcd.clear()
                lcd.set_cursor(0,0)
                lcd.write_string("AM2320: " f"{temp:.1f}ßC")
                lcd.write_string("\nAM2320: " f"{humidity:.1f} %")
                '''
                #output("Temperature Control: ", f"{temperatureControl}")
                if temperatureControl in "enabled":
                    if  temp <= temperatureLowThreshold:
                        if heaterState == SWITCH_OFF:
                            heaterState = SWITCH_ON
                            cmd_output("Heater switched ON")
                    elif temp >= temperatureHighThreshold:
                        if heaterState == SWITCH_ON:
                            heaterState = SWITCH_OFF
                            cmd_output("Heater switched OFF")
                    heaterSwitch.value(heaterState)

                if humidityControl in "enabled":
                    if  humidity >= humidityHighThreshold:
                        if dehumidifierState == SWITCH_OFF:
                            dehumidifierState = SWITCH_ON
                            cmd_output("Dehumidifier switched ON")
                    elif humidity <= humidityHighThreshold:
                        if dehumidifierState == SWITCH_ON:
                            dehumidifierState = SWITCH_OFF
                            cmd_output("Dehumidifier switched OFF")
                    dehumidifierSwitch.value(dehumidifierState)
                                
                if (interval >= postInterval):
                    interval = 1
                    if wifi.wlan.isconnected():
                        gc.collect()
                        current_json_data = build_json_data()
                        ordered_dict = dict(current_json_data) # ...for printout order only...
                        cmd_output("json data: ", json.dumps(ordered_dict))
                        if read_config()["url"] != "test":
                            try:
                                output("Sending post request to: ", read_config()["url"])
                                response = requests.post(read_config()["url"], json=current_json_data, timeout=5)
                                output("Status code: ", str(response.status_code))
                            except Exception as e:
                                output("Error sending POST request: ", str(e))
                        else:
                            cmd_output("No URL to send to...")
                    else:
                        cmd_output("Not connected to any network!")
                else:
                    interval += 1
        except Exception as e:
            cmd_output("AM2320 read error: ", str(e))

        await asyncio.sleep(60)
'''
# This code in intended to fetch system instructions given by authorized 
def power_switch_ctrl():
    if wifi.wlan.isconnected():
        try:
            get_respons = requests.get("https://midtskips.no/garasje/api/env/state.txt")
            output("Status code: ", str(get_respons.status_code))
        except Exception as e:
            output("Error sending POST request: ", str(e))
        # is there an operation for execute?
'''
def build_json_data():
    global postInterval
    global heaterState
    global dehumidifierState

    global humidityControl
    global temperatureControl
    global humidityHighThreshold
    global humidityLowThreshold
    global temperatureLowThreshold
    global temperatureHighThreshold

    humidity, temperature = am2320_sensor.read()
    if temperature is not None and humidity is not None:
        return {
            "Time": time.time(),
            "Humidity": humidity,
            "Temperature": temperature,
            "PostInterval": postInterval,
            "HumidityControl": humidityControl,
            "TemperatureControl": temperatureControl,
            "Dehumidifier":dehumidifierState,
            "Heater":heaterState
        }
    else:
        return {
            "Time": time.time(),
            "Humidity": 0,
            "Temperature": 0,
            "PostInterval": postInterval,
            "HumidityControl":humidityControl,
            "TemperatureControl":temperatureControl,
            "Dehumidifier":dehumidifierState,
            "Heater":heaterState
        }

