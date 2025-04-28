# LED Strip Driver Controller
___Note!___  
The current code fragment may be used for other purposes, so check the ```#define``` definitions before using.  

The C-code software for this Raspberry Pi Pico 2 board is to regulate power to two 3.6 m LED strips (14W/m) by deploying two GPIOs for individual PWM signals which is to control two MOSFET (FQP17N40) transistors.  
The PWM duty cycle are set proportional to the voltage read on two GPIOs configured as analog input.  
The source of the input voltage is the center pin of a linear 10 kΩ potentiometer, which the endpoints are connected to 3.3V and GND.  
The hardware implementation also includes a linear temperature sensor, also connected to a GPIO configured as analog input, to monitor the temperature in the close surroundings.  
A command line user interface over UART (115200 or 9600) is included in order to read system status information.  
