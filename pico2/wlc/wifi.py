import network
from helpers import output

wlan = network.WLAN(network.STA_IF)

def connect_wifi(config):
    wlan.active(True)
    wlan.connect(config["wifi"]["SSID"], config["wifi"]["PASSWORD"])
    
        
    return wlan
