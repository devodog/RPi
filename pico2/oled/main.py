# example.py
from machine import I2C, Pin
import time
from ssd1306_i2c import SSD1306_I2C

# RP Pico 2 I2C pins example (I2C(0) on GP0/GP1 or adjust to your wiring)
i2c = I2C(0, scl=Pin(13), sda=Pin(12), freq=400000)  # change pins if needed
oled = SSD1306_I2C(128, 64, i2c, addr=0x3C)         # use 128x64 or 128x32

oled.fill(0)
oled.text("Hello, Pico 2!", 0, 0)
oled.text("0.98\" OLED", 0, 12)
oled.text("3. Apr 2026", 0, 24)
oled.text("@ Midtskips 10", 0, 36)
oled.text("in Grimstad", 0, 48)

oled.show()
time.sleep(5)
# simple animation
for i in range(0, 200, 5):
    oled.fill(0)
    oled.text("X:" + str(i), 0, 0)
    oled.pixel(64 + i//4, 40, 1)
    oled.show()
    time.sleep(0.1)
