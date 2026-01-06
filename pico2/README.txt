Projects for the Pico 2 family boards

MicroPython projects
====================
wlc = Water Level Control for green house watering system using water resevoirs
and capillary mats. The swoftware monitors two water level sensors placed in 
the reservoirs and when the water level is low, it will open a water valve that
supplies the actual reservoir that has the low water level. The software 
monitors also the temeprature and humidity in the green house.
All of the information. like reservoir water level, valve operation status,
temerature and humidity, is published on midtskips.no/drivhus. 

saunaTemp = Sauna Temeprature Monitor
Consider to change the project name to stm...

htControl = Humidity and Temperature Control is a general system for monitoring and 
controlling that the temperature does not decreas below a cirtain value and
that the humidity does increase above a defined value.
This is done by deploying heater and / or dehumidifier.


C-Code projetcs
===============
led_dim_driver implements adjustable PWM signals to two individual MOSFET sourcing
two individual LED strips for livingroom lightning. The PWM Duty cycle is 
controlled by individual potentiometes where the center terminal is connected
to the pico's ADCs.