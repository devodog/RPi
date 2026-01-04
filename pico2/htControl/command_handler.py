from helpers import *

buffer = b""
def read(pin):
    global buffer
    global monitor
    w = uart0.read()

    if w:
        uart0.write(w)
        buffer += w
        if w == b'\r':
            uart0.write(b'\r\n')
            buf = buffer.decode().strip()
            if buf == "config":
                print_config()
            elif buf == "help":
                print_help()
            elif "url=" in buf or "ssid=" in buf or "password=" in buf:
                change_config(buf)
            elif buf == "version":
                version = read_config()["version"]
                cmd_output("Version: ", version)
            elif buf == "restart":
                cmd_output("Restarting pico...")
                reset()
            elif "humidityHigh=" in buf or "humidityLow=" in buf or "tempHigh=" in buf or "tempLow=" in buf:
                change_config(buf)
            elif "humidityCtrl=" in buf or "tempCtrl" in buf:
                change_config(buf)            
            elif buf == "monitor":
                monitorState("no")
            elif buf == "monitor=on":
                monitorState("on")
            elif buf == "monitor=off":
                monitorState("off")
            # The next commands are mainly for test...
            elif buf == "s1on":
                cmd_output("Switch 1 ON")
                switchCtrl(1, SWITCH_ON)
            elif buf == "s1off":
                cmd_output("Switch 1 OFF")
                switchCtrl(1, SWITCH_OFF)
            elif buf == "s2on":
                cmd_output("Switch 2 ON")
                switchCtrl(2, SWITCH_ON)
            elif buf == "s2off":
                cmd_output("Switch 2 OFF")
                switchCtrl(2, SWITCH_OFF)
            
            uart0.write(b'pico-w> ')
            buffer = b""