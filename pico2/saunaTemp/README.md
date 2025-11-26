## MicroPython project (pico2wifi git-branch) for the Pico w device  
### Indoor humidity and temperature control  
Humidity and temperature monitoring for indoor humidity and temperature control,
by the use of AOSONG AM2320 temperature and humidity i2c sensor, and a simple 
high-level driver in am2320.py.

### i2c connection for the AM2320 on Pico w
SDA to Pico w GPIO xx  
SCL to Pico w GPIO yy  
VDD to 3.3V  
GND to ground  

A 4.7kΩ pull-up resistor between VDD and SDA and SCL.  

-------------------------------------------------------------------------------
### Format of config.json
```
{
    "version": "0.2",
    "wifi":{
        "SSID":"test",
        "PASSWORD":"test",
        "attempts":10,
        "freq":10
    },
    "url":"test"
}
```
