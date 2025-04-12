import utime                    # Módulo de temporização
from machine import Pin, I2C    # GPIO e barramento I2C
from i2c_lcd import I2cLcd      # Classe personalizada para LCD via I2C

# Inicialização do barramento I2C no Raspberry Pi Pico W
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100_000)

# Busca endereço do módulo LCD via scan do I2C
I2C_ADDR = i2c.scan()[0]

# Cria instância do display LCD com 2 linhas e 16 colunas
lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)

def startup_message():
    # Exibe mensagem de boas-vindas com efeito de escrita no LCD
    lcd.clear()
    lcd.move_to(2, 0)
    lcd.putstr("Boas vindas")
    utime.sleep(1)

    lcd.move_to(2, 1)
    message = "Pi2 Safe v0"
    for char in message:
        lcd.putstr(char)
        utime.sleep(0.1)  # Cria animação tipo "máquina de escrever"
    utime.sleep(1)

def wait_screen():
    # Exibe tela de espera com barra de progresso simulada
    lcd.clear()
    lcd.move_to(2, 1)
    lcd.putstr("[          ]")  # Moldura da barra
    lcd.move_to(3, 1)

    for _ in range(10):
        utime.sleep(0.2)
        lcd.putstr(".")  # Simula progresso crescente com pontos