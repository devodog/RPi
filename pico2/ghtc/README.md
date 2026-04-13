# ghtc = Greenhouse Temeprature Control 
This is a MicroPython project on Raspberry Pi Pico board piggyback on a modified LED Strip Driver hardware that was used for a Water Level Control (wlc) unit. The wlc monitored reservoirs for tomato plant watering.  

For the Greenhouse Temperature Control project we'll ommit the reservoir water level detektors and the Sensirion humidity, temperature and CO2 sensor and only use the external onboard analog temperature sensor LM35 from Texas Instruments. The reason for this is that the Sensirion sensor stopped to work at some point - maybe cable issue...
## Recap on the modified LED Strip Driver hardware
<enter picture here>

## Application
The ghtc shall monitor ambient temperature in the greenhouse and switch on or off a heater to regulate the greenhouse temperature.  

### Heater switch control
The LED Strip Driver modified hardware for water level control, provides two optional sources for controlling a mains power switch.  
1. 3.3V Binary MCU output for controlling a triac to close a 230V AC circuit.  
2. 12V - 24V Open Drain n-mosfet circut for controlling a relay that can close a 230V AC circuit.

#### Plan 
Plan #1 is to utilize one of the wired GPIO that is terminated in one of the RJ45 connectors.


### Network access
Pico sends data to url if data has changed, or 15min has passed since last time data was sent

Format of config.json
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
