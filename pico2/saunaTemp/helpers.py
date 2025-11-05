from machine import UART, Pin, reset, I2C
import uasyncio as asyncio
import time
import ntptime
from collections import OrderedDict
import json
from machine import ADC
from lcd_display import LCD
from ds18b20 import DS18B20

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
    print("Turning on valve: ", valve)
    valve.value(1)

def turn_off_valve(valve):
    print("Turning off valve: ", valve)
    valve.value(0)

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


adc2 = ADC(2)
# conversion: ADC.read_u16() -> voltage = value * 3.3 / 65535
# LM35 gives 10 mV/°C so temp_C = voltage / 0.01 = voltage * 100
# Note that the  Basic Centigrade Temperature Sensor (2 °C to 150 °C) starts 
# at 2 °C when the analog input is 0V
_conv_factor = 3.3 / 65535 * 100.0

# Initialize LCD
lcd = LCD()
lastLinePrinted = 0

async def poll_lm35():
    global lastLinePrinted
    while True:
        try:
            raw = adc2.read_u16()
            temp_c = (raw * _conv_factor) - 2
            output("LM35 Temp: ", f"{temp_c:.1f}° C")
            if ((lastLinePrinted == 0) or (lastLinePrinted == 2)):
                lcd.clear()
                lcd.set_cursor(0,0)
                lcd.write_string("LM35: " f"{temp_c:.1f}ß C") # Unicode ß == ° (degrees) on LCD character ROM
                lastLinePrinted = 1
            else:
                lcd.write_string("\nLM35: " f"{temp_c:.1f}ß C") # Unicode ß == ° (degrees) on LCD character ROM
                lastLinePrinted = 2

        except Exception as e:
            cmd_output("LM35 read error: ", str(e))
        await asyncio.sleep(61)

# Initialize DS18B20 on GPIO pin 22
ds_sensor = DS18B20(22)

async def poll_ds18b20():
    global lastLinePrinted
    while True:
        try:
            temp = ds_sensor.read_temp()
            if temp is not None:
                output("DS18B20: ", f"{temp:.1f}° C")
                if (lastLinePrinted == 1):                #lcd.clear()
                    #lcd.set_cursor(0,0)
                    lcd.write_string("\nDS18B20: " f"{temp:.1f}ß C")
                    lastLinePrinted = 2
                else:
                    lcd.clear()
                    lcd.set_cursor(0,0)
                    lcd.write_string("\nDS18B20: " f"{temp:.1f}ß C")
                    lastLinePrinted = 1

        except Exception as e:
            cmd_output("DS18B20 read error: ", str(e))
        await asyncio.sleep(60)

async def read_temp():
    global lastLinePrinted
    while True:
        try:
            raw = adc2.read_u16()
            temp_c = (raw * _conv_factor) - 2
            output("LM35DZ.: ", f"{temp_c:.1f}° C")
            lcd.clear()
            lcd.set_cursor(0,0)
            lcd.write_string("LM35DZ.: " f"{temp_c:.1f}ß C") # Unicode ß == ° (degrees) on LCD character ROM
        except Exception as e:
            cmd_output("LM35 read error: ", str(e))
        
        try:
            temp = ds_sensor.read_temp()
            if temp is not None:
                output("DS18B20: ", f"{temp:.1f}° C")
                lcd.write_string("\nDS18B20: " f"{temp:.1f}ß C")
                lastLinePrinted = 2
        except Exception as e:
            cmd_output("DS18B20 read error: ", str(e))

        await asyncio.sleep(60)
