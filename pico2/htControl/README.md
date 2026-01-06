# MicroPython project for the Pico 2 W device  
Tiny IoT prosjects  
## htControll
__Indoor humidity and temperature control__  
htControl is a RPi Pico w MicroPython project which is to monitor humidity and temperature by the use of a simple humidity and temperature sensor.  
The plan is to control a dehumidifier and heater to prevent freezing temperature within a indoor environment.  

## Hardware brief
Based on Raspberry Pi Pico board mounted on a I/O controller board for interfacing sensors and actuators.  

<img src="./docs/AssemblyGuide.png" height="350">  
Circuit board outline and component placements

Circuit board schematics
Circuit board outline and component placements

Humidity and temperature monitoring for indoor humidity and temperature control,
by the use of AOSONG AM2320 temperature and humidity i2c sensor, and a simple 
high-level driver in am2320.py.

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


### AM2320 drivers
Luckely a driver for the AOSONG AM2320 temperature and humidity i2c sensor, was available ...  




### HTTP POST 
### Temperature and humidity visualization 

### Tests?  
more TBD.