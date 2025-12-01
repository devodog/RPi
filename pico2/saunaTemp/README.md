## MicroPython project (pico2wifi git-branch) for the Pico w device  
### Sauna temerature monitoring  

The Raspberry Pi Pico w board supports a LCD 16x2 character display and the
DS18B20 temperature sensor.

The MicroPython scripts renders the temeprature data and the relativ duration 
of the measurment onto the LCD, in parallel with publishing the measured 
temeprature and local time to a predefined, ref. "url" in the config.json file
listed below, back-end web server.

The MicroPyton scripts also, provides a super simple command-line interface for
debugging and modifying the config file for alternative network connection.

The hardware is interconnected by the use of a single 80 x 60 mm vero-board 
utilizing GPIO 22 for the OneWire connection to the DS18B20 Sensor and
GPIO 16 - 21 for LCD communication (DB4-DB7, Select & Enable) together with a 
10k pot.meter for LCD display adjustments

And 3.3V for UART and OneWire communication and VSYS (5V-0.7V) for power to the
LCD and potmeter for display adjustment.
-------------------------------------------------------------------------------
### Format of config.json
```
{
    "version": "0.1",
    "wifi":{
        "SSID":"test",
        "PASSWORD":"test",
        "attempts":10,
        "freq":10
    },
    "url":"test"
}
```
If url = test, the script will not attempt to send any data to any back-end server.
