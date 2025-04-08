import utime
from machine import Pin, PWM
from lcd_display import lcd

class SmartLock:
    MAX_SERVO_POS = 9000
    MIN_SERVO_POS = 4500
    STEP = 100

    def __init__(self, pin=17):
        self.pwm = PWM(Pin(pin))
        self.pwm.freq(50)
        self.locked = True

    def lock(self):
        lcd.clear()
        lcd.putstr("Bloqueado")
        for pos in range(self.MAX_SERVO_POS, self.MIN_SERVO_POS, -self.STEP):
            self.pwm.duty_u16(pos)
            utime.sleep(0.05)

        self.locked = True
        utime.sleep(1)

    def unlock(self):
        lcd.clear()
        lcd.putstr("Desbloqueado")
        for pos in range(self.MIN_SERVO_POS, self.MAX_SERVO_POS, self.STEP):
            self.pwm.duty_u16(pos)
            utime.sleep(0.05)

        self.locked = False
        utime.sleep(1)

    def toggle(self):
        if self.locked:
            self.unlock()
        else:
            self.lock()