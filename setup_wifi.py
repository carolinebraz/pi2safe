import network
import time

def connect_wifi(ssid, senha):
    print("Conectando-se ao Wi-Fi", end="")  
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(ssid, senha)

    while not sta_if.isconnected():
        print(".", end="")
        time.sleep(0.1)  

    print("\nConectado!")