import gc
import requests
import time
import asyncio
from helpers import *

json_data_sent = {}
current_json_data = {}
last_sent_time = 0  # Track the last time data was sent (in seconds since epoch)

SEND_INTERVAL = 15 * 60  # 15 minutes in seconds

async def send_data():
    global json_data_sent, current_json_data, last_sent_time
    

    while True:
        current_json_data = build_json_data()
        connected = getSensorConnectedStatus()  # Get the current sensor connection status
        if wifi.wlan.isconnected() and connected:
            try:
                gc.collect()
                
                time_since_last_send = time.time() - last_sent_time

                # Send if data has changed OR 15 minutes have passed
                if current_json_data != json_data_sent or time_since_last_send >= SEND_INTERVAL:
                    output("Sending post request to: ", read_config()["url"])
                    response = requests.post(read_config()["url"], json=current_json_data, timeout=5)
                    # for debugging only
                    #import json
                    #output("json sendt: ", json.dumps(current_json_data))
                    #json_data_sent = build_json_data()
                    json_data_sent = current_json_data
                    last_sent_time = time.time()
                    output("Status code: ", str(response.status_code))
                else:
                    pass
                    #output("No change in json data and 15 minutes not passed, will not send")
            except Exception as e:
                output("Error sending POST request: ", str(e))
        else:
            if not wifi.wlan.isconnected():
                output("WiFi not connected, cannot send data.")
            if not connected:
                output("Sensor not connected, cannot send data.")
        await asyncio.sleep(60)  # check every 15 seconds
