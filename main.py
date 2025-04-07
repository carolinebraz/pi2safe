import utime
import gc
from machine import I2C, Pin, PWM

#------------------------- CONFIGURAÇÕES DO HARDWARE -------------------------#
# Display LCD
LCD_CLR             = 0x01
LCD_HOME            = 0x02
LCD_ENTRY_MODE      = 0x04
LCD_ENTRY_INC       = 0x02
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

MASK_RS = 0x01
MASK_RW = 0x02
MASK_E  = 0x04
SHIFT_BACKLIGHT = 3
SHIFT_DATA = 4

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)
I2C_ADDR = i2c.scan()[0]

# Teclado matricial
matrix_keys = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]
keypad_rows = [9, 8, 7, 6]
keypad_columns = [5, 4, 3, 2]
col_pins = [Pin(pin, Pin.IN, Pin.PULL_DOWN) for pin in keypad_columns]
row_pins = [Pin(pin, Pin.OUT) for pin in keypad_rows]
for row_pin in row_pins:
    row_pin.value(1)

# LED
led = Pin(15, Pin.OUT)

# Servo motor
MAX_SERVO_POS = 9000
MIN_SERVO_POS = 4500
STEP = 100
pwm = PWM(Pin(17))
pwm.freq(50)
locked = True

# Arquivo
PIN_FILE = "pin.txt"

#---------------------------------- LCD API -----------------------------------#
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

    def hal_backlight_on(self): pass
    def hal_backlight_off(self): pass
    def hal_write_command(self, cmd): raise NotImplementedError
    def hal_write_data(self, data): raise NotImplementedError
    def hal_sleep_us(self, usecs): utime.sleep_us(usecs)

class I2cLcd(LcdApi):
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

lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)

#---------------------------- INTERFACE DO SISTEMA ----------------------------#
# Tela de boas vindas
def startup_message():
    lcd.clear()
    lcd.move_to(2, 0)
    lcd.putstr("Boas vindas")
    utime.sleep(1)
    lcd.move_to(2, 1)
    msg = "Pi2 Safe v0"
    for char in msg:
        lcd.putstr(char)
        utime.sleep(0.1)
    utime.sleep(1)

# Tela de espera
def wait_screen():
    lcd.clear()
    lcd.move_to(2, 1)
    lcd.putstr("[          ]")
    lcd.move_to(3, 1)
    for _ in range(10):
        utime.sleep(0.2)
        lcd.putstr(".")

def get_key(message):
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr(message)
    lcd.move_to(4, 1)
    lcd.putstr("[______]")
    lcd.move_to(5, 1)

    result = []
    while len(result) < 6:
        for row in range(4):
            row_pins[row].high()
            for col in range(4):
                if col_pins[col].value():
                    key = matrix_keys[row][col]
                    if key:
                        lcd.putstr("*")
                        result.append(key)
                        utime.sleep(0.3)
            row_pins[row].low()

    return "".join(result)

# Configuração inicial
def set_code(pin):
    with open(PIN_FILE, "w") as f:
        f.write(pin)

def get_code():
    try:
        with open(PIN_FILE, "r") as f:
            return f.read().strip()
    except OSError:
        return None

def setup_initial():
        if  get_code() is None:
            new_pin = get_key("Configurar senha")
            lcd.clear()
            lcd.putstr("Salvando...")
            set_code(new_pin)
            utime.sleep(1)
            lcd.clear()
            lcd.putstr("Senha salva!")
            utime.sleep(1)

# Funcionamento do servo motor
def lock():
    global locked
    lcd.clear()
    lcd.putstr("Bloqueado")
    for pos in range(MAX_SERVO_POS, MIN_SERVO_POS, -STEP):
        pwm.duty_u16(pos)
        utime.sleep(0.05)

    locked = True
    utime.sleep(1)

def unlock():
    global locked
    lcd.clear()
    lcd.putstr("Desbloqueado")
    for pos in range(MIN_SERVO_POS, MAX_SERVO_POS, STEP):
        pwm.duty_u16(pos)
        utime.sleep(0.05)

    locked = False
    utime.sleep(1)

def toggle():
    if locked:
        unlock()
    else:
        lock()

# Verificação da senha
def input_code():
    return get_key("Digite a senha:")

def check_pin(guess):
        stored_pin = get_code()

        lcd.clear()
        lcd.putstr("Verificando...")
        utime.sleep(1)
        wait_screen()
        lcd.clear()
        utime.sleep(0.8)

        if guess == stored_pin:
            toggle()
            return True
        else:
            lcd.putstr("Acesso negado!")
            led.on()
            utime.sleep(0.5)
            led.off()
            return False

#----------------------------- EXECUÇÃO DO SISTEMA ----------------------------#
def main():
    startup_message()
    setup_initial()

    while True:
        guess = input_code()
        check_pin(guess)
        utime.sleep(0.5)

if __name__ == "__main__":
    main()