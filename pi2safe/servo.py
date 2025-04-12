import utime                    # Módulo de temporização
from machine import Pin, PWM    # Controle de pinos e sinal PWM para o servo motor
from lcd_display import lcd     # Instância do display LCD
from umqtt import MQTTClient    # Cliente MQTT para comunicação em rede

class SmartLock:
    # Classe para o controle da fechadura inteligente

    MAX_SERVO_POS = 9000  # Posição máxima do servo (desbloqueado)
    MIN_SERVO_POS = 4500  # Posição mínima do servo (bloqueado)
    STEP = 100            # Incremento para movimentação progressiva

    def __init__(self, client: MQTTClient, pin=17):
        # Inicializa o controle do servo motor e configura cliente MQTT
        # Args:
            # client (MQTTClient): instância já conectada ao broker MQTT
            # pin (int): GPIO usado para PWM do servo (padrão = 17)

        self.client = client
        self.pwm = PWM(Pin(pin))
        self.pwm.freq(50)          # Frequência padrão para servo SG90
        self.locked = True         # Estado inicial da fechadura (bloqueada)

    def publish_status(self, status):
        # Publica o status atual da fechadura via MQTT no tópico 'pi2safe/status'
        # Args:
            # status (str): mensagem de status a ser publicada

        if self.client.is_connected():
            self.client.publish("pi2safe/status", status)
        else:
            print("Erro: cliente MQTT desconectado! Tentando reconectar...")
            self.client.connect()
            self.client.publish("pi2safe/status", status)

    def lock(self):
        # Bloqueia a fechadura fisicamente e publica status
        lcd.clear()
        lcd.putstr("Bloqueado")

        # Movimento suave do servo para posição de bloqueio
        for pos in range(self.MAX_SERVO_POS, self.MIN_SERVO_POS, -self.STEP):
            self.pwm.duty_u16(pos)
            utime.sleep(0.05)

        self.publish_status("BLOQUEADO")
        self.locked = True
        utime.sleep(1)

    def unlock(self):
        # Desbloqueia a fechadura fisicamente e publica status
        lcd.clear()
        lcd.putstr("Desbloqueado")

        # Movimento suave do servo para posição de desbloqueio
        for pos in range(self.MIN_SERVO_POS, self.MAX_SERVO_POS, self.STEP):
            self.pwm.duty_u16(pos)
            utime.sleep(0.05)

        self.publish_status("DESBLOQUEADO")
        self.locked = False
        utime.sleep(1)

    def toggle(self):
        # Alterna entre estado bloqueado e desbloqueado
        if self.locked:
            self.unlock()
        else:
            self.lock()