import usocket as socket
import ustruct as struct
import utime
import machine
from ubinascii import hexlify

class MQTTException(Exception):
    pass

class MQTTClient:
    def __init__(self, server="test.mosquitto.org", port=8883, keepalive=60, ssl=False, ssl_params={}):
        self.client_id = "pi2safe" + hexlify(machine.unique_id()).decode()
        self.server = server
        self.port = 8883 if ssl else port
        self.ssl = ssl
        self.ssl_params = ssl_params
        self.keepalive = keepalive
        self.sock = None
        self.cb = None

    def set_callback(self, callback_function):
        self.cb = callback_function

    def is_connected(self):
        return self.sock is not None

    def connect(self):
        print("Conectando-se ao broker MQTT...")
        for _ in range(5):
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                addr = socket.getaddrinfo(self.server, self.port)[0][-1]
                self.sock.connect(addr)

                if self.ssl:
                    import ussl
                    self.sock = ussl.wrap_socket(self.sock, **self.ssl_params)

                print("MQTT conectado!")
                return True

            except Exception as e:
                print(f"Erro ao conectar: {e}. Tentando novamente...")
                utime.sleep(2)

        print("Falha ao conectar após múltiplas tentativas.")
        return False

    def publish(self, topic, msg):
        if not self.is_connected() and not self.connect():
            return False

        try:
            packet = bytearray([0x30])
            topic, msg = topic.encode(), msg.encode()
            remaining_length = len(topic) + len(msg) + 2
            packet.extend(struct.pack("!B", remaining_length))
            packet.extend(struct.pack("!H", len(topic)))
            packet.extend(topic)
            packet.extend(msg)

            self.sock.send(packet)
            print(f"{topic.decode()}: {msg.decode()}")
            return True
        except Exception as e:
            print(f"Erro ao publicar: {e}")
            self.connect()
            return False