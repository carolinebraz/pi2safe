import uos
import utime
from machine import Pin
from keypad import get_key
from servo import SmartLock
from lcd_display import lcd, wait_screen
from umqtt import MQTTClient
from hashlib import sha256

class SecurityManager:
    PIN_FILE = "pin.txt"
    MAX_FAILED_ATTEMPTS = 3
    BASE_WAIT_TIME = 15

    def __init__(self, client: MQTTClient):
        self.client = client
        self.failed_attempts = 0
        self.led = Pin(15, Pin.OUT)
        self.lock = SmartLock(client)

    def hash_code(self, code):
        return sha256(code.encode()).digest()

    def set_code(self, pin):
        hashed_pin = str(self.hash_code(pin))
        with open(self.PIN_FILE, "w") as f:
            f.write(hashed_pin)

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
        stored_hash = self.get_code()
        guess_hash = str(self.hash_code(guess))

        lcd.clear()
        lcd.putstr("Verificando...")
        utime.sleep(1)
        wait_screen()
        lcd.clear()
        utime.sleep(0.8)

        if guess_hash == stored_hash:
            self.lock.toggle()
            self.failed_attempts = 0
            return True
        else:
            self.failed_attempts += 1
            lcd.putstr("Acesso negado!")
            self.led.value(1)
            utime.sleep(0.5)
            self.led.value(0)
            self.client.publish("pi2safe/status", "ACESSO_NEGADO")

            if self.failed_attempts % self.MAX_FAILED_ATTEMPTS == 0:
                wait_time = self.BASE_WAIT_TIME * (2 ** (self.failed_attempts // self.MAX_FAILED_ATTEMPTS))
                lcd.clear()
                for t in range(wait_time, 0, -1):
                    lcd.move_to(0, 0)
                    lcd.putstr("Limite excedido!")
                    lcd.move_to(2, 1)
                    if t < 10:
                        lcd.putstr(f"Aguarde {t} ")
                    else:
                        lcd.putstr(f"Aguarde {t} s")
                    utime.sleep(1)
            
            return False