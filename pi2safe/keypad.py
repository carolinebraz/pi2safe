import utime                    # Módulo de temporização
from machine import Pin         # Controle dos pinos GPIO
from lcd_display import lcd     # Instância do display LCD via I2C

# Matriz de teclas do teclado 4x4 (linhas × colunas)
matrix_keys = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

# Pinos físicos conectados às linhas e colunas do teclado
keypad_rows = [9, 8, 7, 6]      # GPIOs das linhas
keypad_columns = [5, 4, 3, 2]   # GPIOs das colunas

# Configura os pinos das colunas como entradas com resistor pull-down
col_pins = [Pin(pin, Pin.IN, Pin.PULL_DOWN) for pin in keypad_columns]

# Configura os pinos das linhas como saídas
row_pins = [Pin(pin, Pin.OUT) for pin in keypad_rows]

# Ativa todas as linhas inicialmente para leitura
for row_pin in row_pins:
    row_pin.value(1)

# Função que exibe uma mensagem no LCD e lê 6 teclas pressionadas
def get_key(message):
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr(message)           # Linha superior com mensagem de orientação

    lcd.move_to(4, 1)
    lcd.putstr("[______]")        # Moldura visual para a senha
    lcd.move_to(5, 1)             # Posiciona cursor dentro da moldura

    result = []  # Lista para armazenar os caracteres digitados

    # Loop até que 6 teclas sejam capturadas
    while len(result) < 6:
        for row in range(4):           # Percorre linhas
            row_pins[row].high()       # Ativa linha atual
            for col in range(4):       # Percorre colunas
                if col_pins[col].value():           # Se botão estiver pressionado
                    key = matrix_keys[row][col]     # Captura o caractere correspondente
                    if key:
                        lcd.putstr("*")             # Exibe "*" para ocultar o caractere
                        result.append(key)          # Salva tecla
                        utime.sleep(0.3)            # Delay para evitar leitura duplicada
            row_pins[row].low()        # Desativa linha atual após varredura

    return "".join(result)  # Retorna string com os 6 caracteres digitados