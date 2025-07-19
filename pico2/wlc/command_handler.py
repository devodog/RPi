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
                uart0.write(b"WiFi config: " + b"\r\n\t- SSID: " + read_config()["wifi"]["SSID"].encode() + b"\r\n\t- Password: " + read_config()["wifi"]["PASSWORD"].encode() + b"\r\n")
            elif buf == "help":
                cmd_output("Help menu:\r\n-------------------------" \
                "\r\nconfig \t Shows WiFi config" \
                "\r\nstatus \t Shows status of sensors and valves" \
                "\r\nssid:<ssid> \t Changes SSID to <ssid>" \
                "\r\npwd:<pwd> \t Changes PASSWORD to <pwd>" \
                "\r\nrestart: \t Restarts the pico" \
                "\r\nversion \t Shows current version")
            
            elif buf == "status":
                cmd_output("Not implemented yet\r\n")
                #cmd_output(json_data)
            
            elif "ssid:" in buf:
                cmd_output("Old ssid: ", read_config()["wifi"]["SSID"])
                
                # Write updated config
                with open("config.json", "w") as f:
                    config = read_config()
                    config["wifi"]["SSID"] = buf.split(":")[1]
                    json.dump(config, f)

                cmd_output("New ssid: ", read_config()["wifi"]["SSID"])

            elif "pwd:" in buf:
                cmd_output("Old password: ", read_config()["wifi"]["PASSWORD"])
                
                # Write updated config
                with open("config.json", "w") as f:
                    config = read_config()
                    config["wifi"]["PASSWORD"] = buf.split(":")[1]
                    json.dump(config, f)

                cmd_output("New password: ", read_config()["wifi"]["PASSWORD"])
            elif buf == "version":
                version = read_config()["version"]
                cmd_output("Version: ", version)
            elif buf == "wifi":
                cmd_output("IP Address: ", wifi.wlan.ifconfig()[0] if wifi.wlan.isconnected() else 'not connected')
            elif buf == "restart":
                uart0.write(b"Restarting...\r\n")
                reset()  # Restart the microcontroller
            elif buf == "shutdown":
                uart0.write(b"Shutting down...\r\n")
                sys.exit()  # Stop the script
            buffer = b""
            uart0.write(b'pico-w> ')

