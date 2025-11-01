## -*- coding: utf-8 -*-
from machine import Pin
from time import sleep_ms, sleep_us

class LCD:
    def __init__(self):
        # Define pins (GP16 = SR / RS, GP17 = EN, GP18-21 = DB4-DB7)
        self.rs = Pin(16, Pin.OUT)
        self.en = Pin(17, Pin.OUT)
        self.d4 = Pin(18, Pin.OUT)
        self.d5 = Pin(19, Pin.OUT)
        self.d6 = Pin(20, Pin.OUT)
        self.d7 = Pin(21, Pin.OUT)

        # Ensure known idle states
        self.rs.value(0)
        self.en.value(0)
        for p in (self.d4, self.d5, self.d6, self.d7):
            p.value(0)

        # Initialize display
        self.init_display()

    def init_display(self):
        # Wait for power-up
        sleep_ms(50)

        # Initialization sequence for 4-bit interface (send upper nibble only)
        self.rs.value(0)
        self.write4bits(0x03)
        sleep_ms(5)
        self.write4bits(0x03)
        sleep_us(150)
        self.write4bits(0x03)
        sleep_us(150)
        self.write4bits(0x02)  # Set 4-bit mode
        sleep_us(150)

        # Function set: 4-bit, 2 lines, 5x8 dots
        self.command(0x28)
        # Display control: display on, cursor off, blink off
        self.command(0x0C)
        # Clear display
        self.command(0x01)
        sleep_ms(2)
        # Entry mode: increment, no shift
        self.command(0x06)

    def write4bits(self, value):
        # value is 0..15 mapped to D4..D7
        self.d4.value(value & 0x01)
        self.d5.value((value >> 1) & 0x01)
        self.d6.value((value >> 2) & 0x01)
        self.d7.value((value >> 3) & 0x01)
        self.pulse_enable()

    def pulse_enable(self):
        # Short enable pulse; HD44780 needs >= 450ns E high, wait afterwards
        self.en.value(0)
        sleep_us(1)
        self.en.value(1)
        sleep_us(10)   # keep E high for a couple microseconds
        self.en.value(0)
        sleep_us(100)  # wait for instruction to settle

    def command(self, cmd):
        self.rs.value(0)
        self.write4bits((cmd >> 4) & 0x0F)
        self.write4bits(cmd & 0x0F)
        # longer delay for clear/home
        if cmd == 0x01 or cmd == 0x02:
            sleep_ms(2)
        else:
            sleep_us(50)

    def write_char(self, char):
        self.rs.value(1)
        val = ord(char)
        self.write4bits((val >> 4) & 0x0F)  # writing the high side tuple 
        self.write4bits(val & 0x0F)         # writing the low side tuple
        
        sleep_us(100)

    def write_string(self, text):
        # handle newline -> move to second line
        col = 0
        row = 0
        for ch in text:
            if ch == '\n':
                row = 1
                col = 0
                self.set_cursor(row, col)
                continue
            self.write_char(ch)
            col += 1
            if col >= 16:
                # wrap to next line if available
                row = min(row + 1, 1)
                col = 0
                self.set_cursor(row, col)

    def clear(self):
        self.command(0x01)
        sleep_ms(2)

    def set_cursor(self, row, col):
        offsets = [0x00, 0x40]
        addr = offsets[row] + col
        self.command(0x80 | addr)