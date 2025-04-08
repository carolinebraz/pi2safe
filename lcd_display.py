import utime
from machine import Pin, I2C
from i2c_lcd import I2cLcd

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)
I2C_ADDR = i2c.scan()[0]
lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)

def startup_message():
    lcd.clear()
    lcd.move_to(2, 0)
    lcd.putstr("Boas vindas")
    utime.sleep(1)

    lcd.move_to(2, 1)
    message = "Pi2 Safe v0"
    for char in message:
        lcd.putstr(char)
        utime.sleep(0.1)
    utime.sleep(1)

def wait_screen():
    lcd.clear()
    lcd.move_to(2, 1)
    lcd.putstr("[          ]")
    lcd.move_to(3, 1)

    for _ in range(10):
        utime.sleep(0.2)
        lcd.putstr(".")