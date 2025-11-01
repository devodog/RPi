Some info about the DS... temperature sensor driver provided by Claude Sonnet 3.5.
To use this code:

Save the first block as ds18b20.py in your project directory
Add the imports and code changes to your helpers.py
Make sure to import the DS18B20 class in helpers.py:
Key features of this implementation:

Supports multiple DS18B20 sensors on the same bus
Handles errors gracefully
Rounds temperatures to 1 decimal place
Uses async/await for non-blocking operation
Compatible with your existing output and LCD display code
The DS18B20 should be connected as follows:

Data pin to GPIO 22 (can be changed in the initialization)
VDD to 3.3V
GND to ground
A 4.7kΩ pull-up resistor between VDD and the data pin
You can then use either poll_ds18b20() or poll_lm35() in your main async loop, 
depending on which sensor you want to use.

-------------------------------------------------------------------------------
Pico sends data to url if data has changed, or 15min has passed since last time 
data was sent


SCD30 driver: https://github.com/agners/micropython-scd30


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
