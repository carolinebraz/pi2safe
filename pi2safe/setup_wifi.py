import network  # Gerencia interfaces de rede (STA = estação, AP = ponto de acesso)
import time     # Módulo de temporização

# Função que conecta o Raspberry Pi Pico W à rede Wi-Fi
def connect_wifi(ssid, senha):
    print("Conectando-se ao Wi-Fi", end="") # Mensagem inicial para o usuário

    sta_if = network.WLAN(network.STA_IF)   # Cria interface de rede no modo estação (cliente)
    sta_if.active(True)                     # Ativa o Wi-Fi do dispositivo
    sta_if.connect(ssid, senha)             # Tenta conectar com as credenciais fornecidas

    # Aguarda até que a conexão seja estabelecida
    while not sta_if.isconnected():
        print(".", end="")                  # Imprime "." para indicar progresso
        time.sleep(0.1)                     # Breve pausa para evitar travamento

    print("\nConectado!")                   # Confirma conexão concluída