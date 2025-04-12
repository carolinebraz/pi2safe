import usocket as socket       # Módulo de rede com suporte a TCP/IP
import ustruct as struct       # Manipulação binária para montagem de pacotes MQTT
import utime                   # Módulo de temporização
import machine                 # Identificação única do dispositivo
from ubinascii import hexlify  # Codificação hexadecimal do ID do dispositivo

# Exceção personalizada para erros MQTT
class MQTTException(Exception):
    pass

class MQTTClient:
    # Classe de cliente MQTT

    def __init__(self, server="test.mosquitto.org", port=8883, keepalive=60, ssl=False, ssl_params={}):
        # Inicializa o cliente MQTT.
        # Args:
            # server (str): endereço do broker MQTT
            # port (int): porta de comunicação (8883 para SSL, 1883 sem SSL)
            # keepalive (int): tempo de vida da conexão (em segundos)
            # ssl (bool): se deve usar conexão segura (TLS/SSL)
            # ssl_params (dict): parâmetros extras de SSL

        self.client_id = "pi2safe" + hexlify(machine.unique_id()).decode()  # ID único baseado no dispositivo
        self.server = server
        self.port = 8883 if ssl else port
        self.ssl = ssl
        self.ssl_params = ssl_params
        self.keepalive = keepalive
        self.sock = None
        self.cb = None

    def is_connected(self):
        # Verifica se o socket está ativo
        return self.sock is not None

    def connect(self):
        # Tenta conectar ao broker MQTT (até 5 tentativas)

        print("Conectando-se ao broker MQTT...")
        for _ in range(5):
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Cria socket TCP
                addr = socket.getaddrinfo(self.server, self.port)[0][-1]
                self.sock.connect(addr)  # Estabelece conexão com o broker

                if self.ssl:
                    import ussl
                    self.sock = ussl.wrap_socket(self.sock, **self.ssl_params)  # Criptografa conexão

                print("MQTT conectado!")
                return True

            except Exception as e:
                print(f"Erro ao conectar: {e}. Tentando novamente...")
                utime.sleep(2)

        print("Falha ao conectar após múltiplas tentativas.")
        return False

    def publish(self, topic, msg):
        # Publica uma mensagem no tópico especificado usando protocolo MQTT
        # Args:
            # topic (str): tópico MQTT
            # msg (str): mensagem a ser publicada
        # Returns:
            # bool: True se enviado com sucesso, False caso contrário
        
        if not self.is_connected() and not self.connect():
            return False

        try:
            packet = bytearray([0x30])  # MQTT publish

            topic, msg = topic.encode(), msg.encode()
            remaining_length = len(topic) + len(msg) + 2  # Tamanho total do payload

            # Montagem manual do pacote MQTT
            packet.extend(struct.pack("!B", remaining_length))     # Tamanho restante
            packet.extend(struct.pack("!H", len(topic)))           # Tamanho do tópico
            packet.extend(topic)                                   # Tópico
            packet.extend(msg)                                     # Mensagem

            self.sock.send(packet)  # Envia o pacote pelo socket
            print(f"{topic.decode()}: {msg.decode()}")
            return True

        except Exception as e:
            print(f"Erro ao publicar: {e}")
            self.connect()  # Tenta reconectar automaticamente
            return False