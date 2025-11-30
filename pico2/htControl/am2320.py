from machine import I2C
import time

class AM2320:
    """Driver for AOSONG AM2320 temperature and humidity sensor"""
    
    def __init__(self, i2c, address=0x5C):
        """Initialize AM2320 sensor
        
        Args:
            i2c: Initialized I2C object
            address: I2C address of sensor (default 0x5C)
        """
        self.i2c = i2c
        self.address = address
        
    def _crc16(self, data):
        """Calculate CRC16 for data validation"""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc

    def read(self):
        """Read temperature and humidity from sensor
        
        Returns:
            tuple: (humidity, temperature) or (None, None) on error
        """
        try:
            # Wake up sensor
            try:
                self.i2c.writeto(self.address, b'')
            except:
                pass
            
            time.sleep_ms(10)  # Wait for sensor to wake up
            
            # Send read command
            self.i2c.writeto(self.address, bytes([0x03, 0x00, 0x04]))
            
            time.sleep_ms(2)  # Wait for measurement
            
            # Read data
            data = self.i2c.readfrom(self.address, 8)
            
            # Validate response
            if data[0] != 0x03 or data[1] != 0x04:
                return None, None
                
            # Check CRC
            received_crc = (data[7] << 8) | data[6]
            calculated_crc = self._crc16(data[0:6])
            if received_crc != calculated_crc:
                return None, None
                
            # Convert readings
            humidity = (data[2] << 8 | data[3]) / 10.0
            temperature = (data[4] << 8 | data[5]) / 10.0
            
            # Handle negative temperatures
            if temperature > 320:
                temperature = temperature - 655.36
                
            return humidity, temperature
            
        except Exception as e:
            print("Error reading AM2320:", str(e))
            return None, None

# Example usage:
'''
from machine import I2C, Pin

# Initialize I2C with appropriate pins
i2c = I2C(1, scl=Pin(3), sda=Pin(2))  # Adjust pins as needed
sensor = AM2320(i2c)

humidity, temperature = sensor.read()
if humidity is not None and temperature is not None:
    print(f"Humidity: {humidity:.1f}%")
    print(f"Temperature: {temperature:.1f}°C")
else:
    print("Failed to read sensor")
'''