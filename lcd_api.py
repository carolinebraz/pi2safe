import time

LCD_CLR             = 0x01
LCD_HOME            = 0x02

LCD_ENTRY_MODE      = 0x04
LCD_ENTRY_INC       = 0x02
LCD_ENTRY_SHIFT     = 0x01

LCD_ON_CTRL         = 0x08
LCD_ON_DISPLAY      = 0x04
LCD_ON_CURSOR       = 0x02
LCD_ON_BLINK        = 0x01

LCD_MOVE            = 0x10
LCD_MOVE_DISP       = 0x08
LCD_MOVE_RIGHT      = 0x04

LCD_FUNCTION        = 0x20
LCD_FUNCTION_8BIT   = 0x10
LCD_FUNCTION_2LINES = 0x08
LCD_FUNCTION_10DOTS = 0x04
LCD_FUNCTION_RESET  = 0x30

LCD_CGRAM           = 0x40
LCD_DDRAM           = 0x80

class LcdApi:
    def __init__(self, num_lines, num_columns):
        self.num_lines = min(num_lines, 4)
        self.num_columns = min(num_columns, 40)
        self.cursor_x = 0
        self.cursor_y = 0
        self.implied_newline = False
        self._backlight = True

        self.display_off()
        self.backlight = True
        self.clear()
        self.hal_write_command(LCD_ENTRY_MODE | LCD_ENTRY_INC)
        self.hide_cursor()
        self.display_on()

    @property
    def backlight(self):
        return self._backlight

    @backlight.setter
    def backlight(self, value):
        self._backlight = value
        if value:
            self.hal_backlight_on()
        else:
            self.hal_backlight_off()

    def clear(self):
        self.hal_write_command(LCD_CLR)
        self.hal_write_command(LCD_HOME)
        self.cursor_x = 0
        self.cursor_y = 0

    def show_cursor(self):
        self.hal_write_command(LCD_ON_CTRL | LCD_ON_DISPLAY | LCD_ON_CURSOR)

    def hide_cursor(self):
        self.hal_write_command(LCD_ON_CTRL | LCD_ON_DISPLAY)

    def blink_cursor_on(self):
        self.hal_write_command(LCD_ON_CTRL | LCD_ON_DISPLAY | LCD_ON_CURSOR | LCD_ON_BLINK)

    def blink_cursor_off(self):
        self.hal_write_command(LCD_ON_CTRL | LCD_ON_DISPLAY | LCD_ON_CURSOR)

    def display_on(self):
        self.hal_write_command(LCD_ON_CTRL | LCD_ON_DISPLAY)

    def display_off(self):
        self.hal_write_command(LCD_ON_CTRL)

    def move_to(self, cursor_x, cursor_y):
        self.cursor_x = cursor_x
        self.cursor_y = cursor_y
        addr = cursor_x & 0x3F
        if cursor_y & 1:
            addr += 0x40
        if cursor_y & 2:
            addr += self.num_columns
        self.hal_write_command(LCD_DDRAM | addr)

    def putchar(self, char):
        if char == '\n':
            if not self.implied_newline:
                self.cursor_x = self.num_columns
        else:
            self.hal_write_data(ord(char))
            self.cursor_x += 1

        if self.cursor_x >= self.num_columns:
            self.cursor_x = 0
            self.cursor_y += 1
            self.implied_newline = (char != '\n')

        if self.cursor_y >= self.num_lines:
            self.cursor_y = 0

        self.move_to(self.cursor_x, self.cursor_y)

    def putstr(self, string):
        for char in string:
            self.putchar(char)

    def custom_char(self, location, charmap):
        location &= 0x7
        self.hal_write_command(LCD_CGRAM | (location << 3))
        for i in range(8):
            self.hal_write_data(charmap[i])
            self.hal_sleep_us(40)
        self.move_to(self.cursor_x, self.cursor_y)

    def hal_backlight_on(self):
        pass

    def hal_backlight_off(self):
        pass

    def hal_write_command(self, cmd):
        raise NotImplementedError

    def hal_write_data(self, data):
        raise NotImplementedError

    def hal_sleep_us(self, usecs):
        time.sleep_us(usecs)