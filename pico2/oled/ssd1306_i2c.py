# ssd1306_i2c.py
from machine import I2C
import framebuf
import time

# Basic SSD1306 driver for 128x64 or 128x32 displays
class SSD1306_I2C:
    def __init__(self, width, height, i2c, addr=0x3C):
        self.width = width
        self.height = height
        self.i2c = i2c
        self.addr = addr
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        self.framebuf = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self.init_display()

    def write_cmd(self, cmd):
        self.i2c.writeto(self.addr, b'\x00' + bytes([cmd]))

    def init_display(self):
        for cmd in (
            0xAE,             # display off
            0x20, 0x00,       # memory addressing mode: horizontal
            0xB0,             # page start address
            0xC8,             # COM output scan direction remapped
            0x00,             # low col addr
            0x10,             # high col addr
            0x40,             # start line = 0
            0x81, 0x7F,       # contrast
            0xA1,             # seg remap
            0xA6,             # normal display (A7 = inverse)
            0xA8, self.height - 1,  # multiplex ratio
            0xA4,             # display follows RAM
            0xD3, 0x00,       # display offset
            0xD5, 0x80,       # display clock divide
            0xD9, 0xF1,       # pre-charge
            0xDA, 0x12,       # COM pins config (0x12 for 128x64, 0x02 for some 128x32)
            0xDB, 0x40,       # vcom detect
            0x8D, 0x14,       # charge pump on
            0xAF              # display on
        ):
            self.write_cmd(cmd)
        self.fill(0)
        self.show()

    # Framebuffer helpers
    def fill(self, color):
        self.framebuf.fill(color)

    def pixel(self, x, y, color):
        self.framebuf.pixel(x, y, color)

    def text(self, string, x, y, color=1):
        self.framebuf.text(string, x, y, color)

    def blit(self, fbuf, x, y):
        self.framebuf.blit(fbuf, x, y)

    # Send buffer to display
    def show(self):
        for page in range(0, self.pages):
            self.write_cmd(0xB0 + page)                    # set page
            self.write_cmd(0x00)                           # set low col
            self.write_cmd(0x10)                           # set high col
            start = page * self.width
            chunk = self.buffer[start:start + self.width]
            # Control byte 0x40 for data
            self.i2c.writeto(self.addr, b'\x40' + chunk)

    # Optional: invert display
    def invert(self, invert):
        self.write_cmd(0xA7 if invert else 0xA6)
