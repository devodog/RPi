from machine import UART, Pin, reset
import time
from lcd_display import LCD

uart0 = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))

# This pin assignment is ONLY valid for code on the water level control system (wlc)
#powerSwitch1 = Pin(16, Pin.OUT)
#powerSwitch2 = Pin(17, Pin.OUT)

def output(text, arg="", delay=0.1):    
    local_time = get_local_timestamp(1) # one hour different from gmt at winter-time? 
    uart0.write(b'[' + local_time.encode() + b'] ' + text.encode() + arg.encode() + b'\r\n')
    time.sleep(delay)

def cmd_output(text, arg="", delay=0.1):
    uart0.write(text.encode() + arg.encode() + b'\r\n')
    time.sleep(delay)

def print_help():
    help_text = (
    "\nHelp menu:\r\n"
    "-------------------------\r\n"
    "info               \tShows info about the system\r\n"
    "restart            \tRestarts the pico\r\n"
    "version            \tShows current version")
    cmd_output(help_text)
    cmd_output("")

def get_local_timestamp(offset_hours=0):
    t = time.localtime(time.time() + offset_hours * 3600)
    return f"{t[0]:04}-{t[1]:02}-{t[2]:02} {t[3]:02}:{t[4]:02}:{t[5]:02}"

# Initialize LCD
lcd = LCD()

def displaySpeed():
    #output("DS18B20: ", f"{temp:.1f}° C")
    lcd.clear()
    lcd.set_cursor(0,0)
    lcd.write_string("Speed: 12.3 km/h")
    lcd.set_cursor(0,1)
    hourMinSec = get_local_timestamp(1)
    lcd.write_string("Startet"f"{hourMinSec[10:]}")
    time.sleep(0.1)
