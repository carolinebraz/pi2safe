import utime                                # Módulo de temporização
import setup_wifi                           # Módulo para conectar à rede Wi-Fi
from lcd_display import startup_message     # Mensagem de boas-vindas no LCD
from security import SecurityManager        # Gerenciador de segurança do sistema
from umqtt import MQTTClient                # Cliente MQTT para comunicação em rede

# Função auxiliar para conectar ao broker MQTT
def connect_mqtt():
    client = MQTTClient()           # Cria instância do cliente MQTT
    if client.connect():            # Tenta conectar ao broker
        return client               # Se sucesso, retorna instância pronta
    else:
        return None                 # Em caso de falha, retorna None

# Função principal que coordena os módulos do sistema
def main():
    startup_message()                           # Exibe mensagem de boas-vindas no LCD
    setup_wifi.connect_wifi("Wokwi-GUEST", "")  # Conecta à rede Wi-Fi simulada

    client = connect_mqtt()                     # Estabelece comunicação com broker MQTT
    if client is None:                          # Falha ao conectar ao broker
        return

    security_manager = SecurityManager(client)  # Inicializa controle de segurança
    security_manager.setup_initial()            # Verifica ou configura senha inicial

    # Loop contínuo para entrada e validação de senha
    while True:
        guess = security_manager.input_code()   # Solicita senha via teclado matricial
        security_manager.check_pin(guess)       # Valida senha e executa ação correspondente
        utime.sleep(0.5)                        # Pausa breve entre tentativas

# Executa o sistema apenas se o script for chamado diretamente
if __name__ == "__main__":
    main()