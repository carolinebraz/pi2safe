import utime
from machine import Pin, PWM
from lcd_display import lcd
from umqtt import MQTTClient

class SmartLock:
    MAX_SERVO_POS = 9000
    MIN_SERVO_POS = 4500
    STEP = 100

    def __init__(self, client: MQTTClient, pin=17):
        self.client = client
        self.pwm = PWM(Pin(pin))
        self.pwm.freq(50)
        self.locked = True

    def publish_status(self, status):
        if self.client.is_connected():
            self.client.publish("pi2safe/status", status)
        else:
            print("Erro: cliente MQTT desconectado! Tentando reconectar...")
            self.client.connect()
            self.client.publish("pi2safe/status", status)

    def lock(self):
        lcd.clear()
        lcd.putstr("Bloqueado")
        for pos in range(self.MAX_SERVO_POS, self.MIN_SERVO_POS, -self.STEP):
            self.pwm.duty_u16(pos)
            utime.sleep(0.05)

        self.publish_status("BLOQUEADO")
        self.locked = True
        utime.sleep(1)

    def unlock(self):
        lcd.clear()
        lcd.putstr("Desbloqueado")
        for pos in range(self.MIN_SERVO_POS, self.MAX_SERVO_POS, self.STEP):
            self.pwm.duty_u16(pos)
            utime.sleep(0.05)

        self.publish_status("DESBLOQUEADO")
        self.locked = False
        utime.sleep(1)

    def toggle(self):
        if self.locked:
            self.unlock()
        else:
            self.lock()