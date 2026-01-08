# MicroPython project for the Pico 2 W device  
Tiny IoT prosjects  
## htControll
__Indoor humidity and temperature control__  
htControl is a RPi Pico w MicroPython project which is to monitor humidity and temperature by the use of a simple humidity and temperature sensor.  
The plan is to control a dehumidifier and heater to prevent freezing temperature within a indoor environment.  

... the following needs to be reviced...
Environment variables to manage dehumidifier and heater
The high threshold, when read from the sensor, will swich ON the dehumidifier.
The low threshold, when read from the sensor, will switch OFF the dehumidifier.
The low temperature threshold, when read from the sensor, will turn ON the heater.
The high temperature threshold, when read from the sensor, will turn OFF the heater.
If the temperature is lower or equal to the Minimum temperature threshold, the heater switch will be activated, if enabled.
When the temperature is 3 to 5 degrees Centigrade over the Minimum temperature threshold, the heater switch will be deactivated.
If the humidity is over or equal to the Maximum humidity threshold, dehumidifier switch will activated, if enabled.
When the humidity is 10 to 20 % lower than the Maximum humidity threshold, the dehumidifier switch will be deactivated.  

## Hardware brief
Based on Raspberry Pi Pico board mounted on a I/O controller board for interfacing sensors and actuators.  

<img src="./docs/AssemblyGuide.png" height="350">

Circuit board outline and component placements  

<img src="./docs/LEDstripDriver.png" height="500">  

Circuit board schematics  

### Monitoring Humidity and temperature
Humidity and temperature monitoring for indoor humidity and temperature control,
by the use of AOSONG AM2320 temperature and humidity i2c sensor, and a simple 
high-level driver in am2320.py.  
<img src="./docs/AOSONG-Sensor.png" height="250">  
AOSONG AM2320 temperature and humidity i2c sensor  

### i2c connection for the AM2320 on Pico 2 W  
The following screw-terminals on the PCB is used for the humidity and temperature sensor:  
- SDA to Pico 2 W GPIO 26 @screw-terminal#1 on __J6__  
- SCL to Pico 2 W GPIO 27 @screw-terminal#2 on __J6__  
- VDD to 3.3V	@screw-terminal#2 on __J5__  
- GND to ground	@screw-terminal#1 on __J5__  
- A 5.6 kΩ pull-up resistor between VDD and SDA and SCL.  

### Monitor and configuration option via Pico UART
To monitor and change system configuration, the board provides a simple UART serial port pin header connector (__J3__), which is wired to Pico's UART0 pins GPIO0 (TX) and GPIO1 (RX).  
The serial port is set to 9600 baud with 1 start-bit, 1 stop-bit and no parity.  
Note that:  
- pin#1 = 3V3
- pin#2 = TX
- pin#3 = RX
- pin#4 = GND  

## Software brief
The software that provides and supports the overall functionality is assembled by a set of Python scripts.    
 
### MicroPyton for Raspberry Pi Pico
The MicroPython Firmware for Raspberry Pi Pico 2 W is downloaded from https://micropython.org/download/RPI_PICO2_W/  

### Basic concept
In general, the system implementation, will launch two asynchronus threads, one for periodically reading the sensor data and one that attempts to keep the wifi connection alive.  
The Pico 2 W device's network connectivity and operation is dependent of a onboard configuration file,  
config.json, which have the following format:
```
{
    "version": "0.1",
    "wifi":{
        "SSID":"someSSID",
        "PASSWORD":"somePASSWORD",
        "attempts":10,
        "freq":10
    },
    "url":"SomeURL"
    "postInt": 5,
    "envctrl":{
        "humidityCtrl":"disabled",
        "tempCtrl":"disabled",
        "humidityHighThreshold":"80",
        "humidityLowThreshold":"70",
        "TemperatureLowThreshold":1,
        "TemperatureHigThreshold":10
    },
}
```  
All of the parameters in this config file is changeable from the Pico 2 W serial port command line interface (UART on GPIO0 and GPIO1).  
The following commends are currently abaliable:  
- help &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;This information
- info &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;Shows info about the system  
- config &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;Shows contents of config.json
- url=\<url> &emsp;&emsp;&emsp;&emsp;&ensp;Changes URL in config.json to \<url>
- postInt=\<int>&emsp;&emsp;&emsp;Number of minutes between POSTs 
- ssid=\<ssid> &emsp;&emsp;&emsp;&ensp;Changes SSID in config.json to \<ssid>
- password=\<pwd>&emsp;Changes PASSWORD in config.json to \<pwd>
- attempts=\<int>&emsp;&emsp;Number of WiFi reconnection attempts (default: 10)
- freq=\<int>&emsp;&emsp;&emsp;&emsp;Sleep interval between each bulk of reconnection attempts (default: 10min)
- restart &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;Restarts the pico
- version&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;Shows current version
- humidityControl=\<enabled | disabled>&emsp;&emsp;&emsp;&ensp;Humidity control ON/OFF
- temperatureControl=\<enabled | disabled>&emsp;&emsp;Temperature control ON/OFF
- humidityHigh=\<int>&emsp;High humidity level threshold for switch ON
- humidityLow=\<int> &emsp;Low humidity level threshold for switch OFF
- tempHigh=\<int>&emsp;&emsp;&ensp;High temperature level threshold for heater OFF
- tempLow=\<int>&emsp;&emsp;&emsp;Low temperature level threshold for heater ON

Example:  
TBD

### AM2320 driver
Luckely a driver for the AOSONG AM2320 temperature and humidity i2c sensor, was available at:  
https://github.com/mcauser/micropython-am2320  
So, minimal effort to integrate this device into the system. Just needed to select SDA and SCL on the Pico board (those that already was wired to two screw-terminals) and import the I2C in addition to other parts needed from the machine library...  

### Publishing environment climate data
As indicated above, the unit monitors the environment it is placed in periodically, and sends the sensor data to a web server.  
The data is sent over the HTTP REST interface by POSTing the sensor values with a timestamp as a json-formated string, formated as follows:  
```
{
    "Timestamp": 1767440462,
    "Measurement": {
        "Humidity": 34.8,
        "Temperature": 20.9
    }
}
```
The above is currently under modification....  

### Humidity and Temperature visualization 
The humidity and temperature is to be rendered graphically showing the humidity and temperature in a time scaled diagram.  
 
### Tests used on Windows
Using a simple test to ensure that the backend is reponding as expected.  
curl -X POST -H "Content-Type: application/json" -d "{\"Time\": 1764772947, \"Humidity\": 71.8, \"Temperature\": 21.8}" "http://someURL"
