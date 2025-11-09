from helpers import *

buffer = b""
def read(pin):
    global buffer
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
                   
            uart0.write(b'pico-w> ')
            buffer = b""