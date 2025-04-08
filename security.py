import utime
from machine import Pin
from keypad import get_key
from servo import SmartLock
from lcd_display import lcd, wait_screen

class SecurityManager:
    PIN_FILE = "pin.txt"

    def __init__(self):
        self.led = Pin(15, Pin.OUT)
        self.lock = SmartLock()

    def set_code(self, pin):
        with open(self.PIN_FILE, "w") as f:
            f.write(pin)

    def get_code(self):
        try:
            with open(self.PIN_FILE, "r") as f:
                return f.read().strip()
        except OSError:
            return None

    def setup_initial(self):
        if self.get_code() is None:
            new_pin = get_key("Configurar senha")
            lcd.clear()
            lcd.putstr("Salvando...")
            self.set_code(new_pin)
            utime.sleep(1)
            lcd.clear()
            lcd.putstr("Senha salva!")
            utime.sleep(1)

    def input_code(self):
        return get_key("Digite a senha:")

    def check_pin(self, guess):
        stored_pin = self.get_code()

        lcd.clear()
        lcd.putstr("Verificando...")
        utime.sleep(1)
        wait_screen()
        lcd.clear()
        utime.sleep(0.8)

        if guess == stored_pin:
            self.lock.toggle()
            return True
        else:
            lcd.putstr("Acesso negado!")
            self.led.on()
            utime.sleep(0.5)
            self.led.off()
            return False