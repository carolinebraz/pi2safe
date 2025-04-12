from umqtt import MQTTClient             # Cliente MQTT para comunicação remota
from security import SecurityManager     # Gerenciador de autenticação

# Instancia o sistema de segurança com comunicação MQTT
client = MQTTClient()
security = SecurityManager(client)

# Simulação de ataque de força bruta
def bfa():
    # Testa múltiplas combinações de senha para verificar a robustez do sistema
    # Primeiro testa senhas comuns, depois gera todas as combinações de 6 dígitos

    # Dicionário de senhas comuns e padronizadas
    common_pins = [
        "123456", "111111", "222222", "333333", "444444",
        "555555", "666666", "777777", "888888", "999999",
        "000000", "123123", "456456", "789789", "101010"
    ]

    # Dígitos válidos para composição de senhas
    possible_digits = "1234567890"

    # Primeiro testa dicionário de senhas comuns
    for pin in common_pins:
        if test_password(security, pin):
            return  # Encerra se encontrar senha válida

    # Depois testa todas as combinações possíveis de 6 dígitos
    for d1 in possible_digits:
        for d2 in possible_digits:
            for d3 in possible_digits:
                for d4 in possible_digits:
                    for d5 in possible_digits:
                        for d6 in possible_digits:
                            code = d1 + d2 + d3 + d4 + d5 + d6
                            if test_password(security, code):
                                return  # Encerra se encontrar senha válida

# Função auxiliar para validar uma senha e exibir o resultado
def test_password(security, pin):
    # Testa uma senha específica usando o método de validação do SecurityManager.
    # Args:
        # security (SecurityManager): instância ativa do gerenciador de segurança
        # pin (str): senha que será testada
    # Returns:
        # bool: True se a senha for válida, False caso contrário

    if security.check_pin(pin):
        print(f"✅ Senha encontrada: {pin}")
        return True
    else:
        print(f"❌ Tentativa de senha {pin} falhou")
        return False