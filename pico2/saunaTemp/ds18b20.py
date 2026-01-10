import time
from machine import Pin
from onewire import OneWire
from ds18x20 import DS18X20

class DS18B20:
    found = False
    def __init__(self, data_pin):
        self.found = False
        """Initialize DS18B20 temperature sensor.
        
        Args:
            data_pin (int): GPIO pin number for data line
        """
        self.dat = Pin(data_pin, Pin.IN, Pin.PULL_UP)
        self.ds = DS18X20(OneWire(self.dat))
        self.roms = self.ds.scan()  # Scan for devices
        
        if not self.roms:
            print("No DS18B20 sensors found")
        else:
            self.found = True
            
    def read_temp(self):
        """Read temperature from the sensor.
        
        Returns:
            float: Temperature in Celsius
        """
        try:
            self.ds.convert_temp()
            # Conversion takes up to 750ms
            #time.sleep_ms(750)
            time.sleep(1)
            
            # Read temperature from first sensor found
            temp = self.ds.read_temp(self.roms[0])
            return round(temp, 1)
            
        except Exception as e:
            print(f"Error reading DS18B20: {str(e)}")
            return None
            
    def read_all_temps(self):
        """Read temperatures from all connected sensors.
        
        Returns:
            list: List of temperatures in Celsius
        """
        try:
            self.ds.convert_temp()
            #time.sleep_ms(750)
            time.sleep(1)
            
            temps = []
            for rom in self.roms:
                temp = self.ds.read_temp(rom)
                temps.append(round(temp, 1))
            return temps
            
        except Exception as e:
            print(f"Error reading DS18B20: {str(e)}")
            return None