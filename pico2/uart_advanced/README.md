# LED Strip Driver Controller
___Note!___  
The current code fragment may be used for other purposes, so check the ```#define``` definitions before using.  

The C-code software for this Raspberry Pi Pico 2 board is to regulate power to two 3.5 m LED strips (14W/m) by using two GPIOs for individual PWM signals which is to control two MOSFET (FQP17N40) transistors.  
The PWM duty cycle are set proportional to the voltage read on two GPIOs configured as analog input.  
The source of the input voltage is the center pin of a linear 10 kΩ potentiometer, which the endpoints are connected to 3.3V and GND.  
The hardware implementation also includes a linear temperature sensor, also connected to a GPIO configured as analog (ADC2) input, to monitor the temperature in the close surroundings of one of the MOSFET.  
A command line user interface over UART (9600) is included in order to read system status information and send simple commands for PWM duty cycle for each LED strip driver.  

## Terminal commands
```led1```  - will give the current PWM duty cycle for the LED strip #1
```
pico2>led1  
ADC0 (LED1) DutyCycle: 15 %  
```  
```led2```  - will give the current PWM duty cycle for the LED strip #2
```
pico2>led2  
ADC1 (LED1) DutyCycle: 15 %  
```  
```temp```  - will give the current temperature near the Q1 MOSFET transistor.  
```
pico2>temp
ADC2 temp: 24.3 C°  
```  
Disabling the potentiometer control if digital control is wanted.  
Enabling the potentiometer if potentiometer control is wanted.  
```pot <on|off>```  - will give the current PWM duty cycle for the LED strip #2
```
pico2>pot off
Potmeter OFF  
```  
```
pico2>pot on
Potmeter ON  
```  
Setting the PWM duty cycle from the terminal if the potentiometer is disabled.  
```dc<1|2> duty cycle>```  - will set the duty cycle for LED strip 1 or 2
```
pico2>dc2 50
ADC1 (LED1) DutyCycle: 15 %  
```  