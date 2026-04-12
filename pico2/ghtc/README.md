# ghtc = Greenhouse Temeprature Control 
This project reuses the Water Level Control (wlc) unit, for automatic tomato plant watering, which in turn was a reuse of the LED strip driver.  

For this project we'll ommit the reservoir water level detektors and the Sensirion humidity, temperature and CO2 sensor and only use the external onboard analog temperature sensor LM35 from Texas Instruments.


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
