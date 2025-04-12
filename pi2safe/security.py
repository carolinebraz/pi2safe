import uos                                  # Gerenciamento de arquivos locais no sistema
import utime                                # Módulo de temporização
from machine import Pin                     # Controle de pinos GPIO
from keypad import get_key                  # Função para entrada via teclado matricial
from servo import SmartLock                 # Controle físico da fechadura
from lcd_display import lcd, wait_screen    # LCD e animação de progresso
from umqtt import MQTTClient                # Comunicação MQTT para status remoto
from hashlib import sha256                  # Criptografia hash para senha

class SecurityManager:
    # Classe responsável pelo controle de senha e lógica de acesso

    PIN_FILE = "pin.txt"            # Arquivo onde a senha é armazenada
    MAX_FAILED_ATTEMPTS = 3         # Tentativas inválidas antes do bloqueio
    BASE_WAIT_TIME = 15             # Tempo inicial de bloqueio (em segundos)

    def __init__(self, client: MQTTClient):
        # Inicializa o gerenciador de segurança
        # Args:
            #client (MQTTClient): instância do cliente MQTT para publicação de status
        
        self.client = client
        self.failed_attempts = 0               # Contador de falhas consecutivas
        self.led = Pin(15, Pin.OUT)            # LED indicador para acesso negado
        self.lock = SmartLock(client)          # Instância da fechadura inteligente

    def hash_code(self, code):
        # Gera hash SHA-256 a partir de uma string de código
        # Args:
            # code (str): senha digitada
        # Returns:
            # bytes: resultado do hash criptográfico

        return sha256(code.encode()).digest()

    def set_code(self, pin):
        # Salva a senha (em formato hash) no arquivo
        # Args:
            # pin (str): senha definida pelo usuário

        hashed_pin = str(self.hash_code(pin))
        with open(self.PIN_FILE, "w") as f:
            f.write(hashed_pin)

    def get_code(self):
        # Recupera o hash da senha armazenado no sistema
        # Returns:
            # str: hash da senha ou None se arquivo não existir

        try:
            with open(self.PIN_FILE, "r") as f:
                return f.read().strip()
        except OSError:
            return None

    def setup_initial(self):
        # Realiza configuração inicial da senha se ainda não existir
        # Exibe tela interativa para entrada e confirmação visual

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
        # Solicita a digitação da senha via teclado matricial
        # Returns:
            # str: sequência de caracteres digitados

        return get_key("Digite a senha:")

    def check_pin(self, guess):
        # Valida a senha digitada contra o hash armazenado
        # Gerencia tentativa, acesso, bloqueio e feedback visual
        # Args:
            # guess (str): senha digitada
        # Returns:
            # bool: True para acesso liberado, False caso contrário
            
        stored_hash = self.get_code()
        guess_hash = str(self.hash_code(guess))

        lcd.clear()
        lcd.putstr("Verificando...")
        utime.sleep(1)
        wait_screen()
        lcd.clear()
        utime.sleep(0.8)

        # Senha correta
        if guess_hash == stored_hash:
            self.lock.toggle()
            self.failed_attempts = 0
            return True

        # Senha incorreta
        else:
            self.failed_attempts += 1
            lcd.putstr("Acesso negado!")
            self.led.value(1)
            utime.sleep(0.5)
            self.led.value(0)

            self.client.publish("pi2safe/status", "ACESSO_NEGADO")

            # Bloqueio progressivo após múltiplas falhas
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