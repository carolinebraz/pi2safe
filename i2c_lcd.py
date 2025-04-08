import utime
import gc
from lcd_api import *
from machine import I2C

MASK_RS = 0x01
MASK_RW = 0x02
MASK_E  = 0x04

SHIFT_BACKLIGHT = 3
SHIFT_DATA = 4

class I2cLcd(LcdApi):
    #Implementa display LCD HD44780 via PCF8574 usando I2C

    def __init__(self, i2c: I2C, i2c_addr: int, num_lines: int, num_columns: int):
        self.i2c = i2c
        self.i2c_addr = i2c_addr

        self._write_byte(0x00)
        utime.sleep_ms(20)

        for _ in range(3):
            self._write_init_nibble(LCD_FUNCTION_RESET)
            utime.sleep_ms(5 if _ == 0 else 1)

        self._write_init_nibble(LCD_FUNCTION)
        utime.sleep_ms(1)

        super().__init__(num_lines, num_columns)

        cmd = LCD_FUNCTION
        if num_lines > 1:
            cmd |= LCD_FUNCTION_2LINES
        self.hal_write_command(cmd)

        gc.collect()

    def hal_write_command(self, cmd: int):
        self._send(cmd, is_data=False)
        if cmd <= 3:
            utime.sleep_ms(5)
        gc.collect()

    def hal_write_data(self, data: int):
        self._send(data, is_data=True)
        gc.collect()

    def hal_backlight_on(self):
        self._write_byte(1 << SHIFT_BACKLIGHT)

    def hal_backlight_off(self):
        self._write_byte(0x00)

    def hal_sleep_us(self, usecs: int):
        utime.sleep_us(usecs)

    def _write_byte(self, byte: int):
        self.i2c.writeto(self.i2c_addr, bytes([byte]))

    def _write_init_nibble(self, nibble: int):
        data = ((nibble >> 4) & 0x0F) << SHIFT_DATA
        self._pulse(data)

    def _send(self, value: int, is_data: bool):
        rs = MASK_RS if is_data else 0x00
        bl = self.backlight << SHIFT_BACKLIGHT
        high = ((value >> 4) & 0x0F) << SHIFT_DATA
        low  = (value & 0x0F) << SHIFT_DATA

        self._pulse(rs | bl | high)
        self._pulse(rs | bl | low)

    def _pulse(self, data: int):
        self._write_byte(data | MASK_E)
        self._write_byte(data)