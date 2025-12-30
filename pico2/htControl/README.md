## MicroPython project for the Pico w device  
Tiny IoT prosjects  
### htControll
__Indoor humidity and temperature control__  
htControl is a RPi Pico w MicroPython project which is to monitor humidity and temperature by the use of a simple humidity and temperature sensor.  
The plan is to control a dehumidifier and heater to prevent freezing temperature within a indoor environment.  

### Hardware brief
Based on Raspberry Pi Pico board mounted on a I/O controller board for interfacing sensors and actuators.
...more will be added...
Humidity and temperature monitoring for indoor humidity and temperature control,
by the use of AOSONG AM2320 temperature and humidity i2c sensor, and a simple 
high-level driver in am2320.py.

### i2c connection for the AM2320 on Pico w
SDA to Pico w GPIO xx  
SCL to Pico w GPIO yy  
VDD to 3.3V  
GND to ground  

A 4.7kΩ pull-up resistor between VDD and SDA and SCL.  