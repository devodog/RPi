## MicroPython project for the Pico w device  
### Tred Mill speed monitoring  

### Hardware
TBD  

### General notes to be refined...
The hardware is interconnected by the use of a single 80 x 60 mm vero-board 

GPIO 16 - 21 for LCD communication (DB4-DB7, Select & Enable) together with a 
10k pot.meter for LCD display adjustments

And 3.3V for UART and VSYS (5V-0.7V) for power to the
LCD and potmeter for display adjustment.

The Raspberry Pi Pico w board supports a LCD 16x2 character display.

The MicroPython scripts renders the tred mill speed onto the LCD.  

The MicroPyton scripts also, provides a super simple command-line interface for
debugging.
