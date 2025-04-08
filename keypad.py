import utime
from machine import Pin
from lcd_display import lcd

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
