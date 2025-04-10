import network
import utime
import setup_wifi
from lcd_display import startup_message
from security import SecurityManager
from umqtt import MQTTClient

def connect_mqtt():
    client = MQTTClient()
    if client.connect():
        return client
    else:
        return None

def main():
    startup_message()
    setup_wifi.connect_wifi("Wokwi-GUEST", "")

    client = connect_mqtt()
    if client is None:
        return

    security_manager = SecurityManager(client)
    security_manager.setup_initial()

    while True:
        guess = security_manager.input_code()
        security_manager.check_pin(guess)
        
        utime.sleep(0.5)

if __name__ == "__main__":
    main()