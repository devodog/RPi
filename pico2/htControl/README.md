htc0 RPi Pico w project is to monitor humidity and temperature by the use of a simple humidity and temperature sensor.  
The plan is to control a dehumidifier and heater to prevent freezing temperature within a indoor environment.  

...more will be added...
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