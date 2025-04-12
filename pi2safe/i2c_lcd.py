# Adaptado do repositório dhylands/python_lcd por Dave Hylands
# Fonte original: https://github.com/dhylands/python_lcd
# Implementação para controle de display LCD HD44780 via PCF8574 usando barramento I2C

import utime                # Módulo de temporização
import gc                   # Coleta de lixo: ajuda a liberar memória após comandos LCD
from lcd_api import *       # Interface base com comandos do LCD HD44780
from machine import I2C     # Biblioteca para controle do barramento I2C no Pico

# Máscaras de bits para controle dos sinais digitais do LCD
MASK_RS = 0x01              # Register Select: 0 = comando, 1 = dados
MASK_RW = 0x02              # Read/Write: 0 = write, 1 = read
MASK_E  = 0x04              # Enable: pulso para registrar comandos/dados

SHIFT_BACKLIGHT = 3         # Bit responsável pelo controle da luz de fundo
SHIFT_DATA = 4              # Bit para posicionar dados nos pinos D4-D7

class I2cLcd(LcdApi):
    # Classe que herda a API genérica LcdApi e implementa o hardware específico via I2C

    def __init__(self, i2c: I2C, i2c_addr: int, num_lines: int, num_columns: int):
        # Inicializa o display e aplica o protocolo de inicialização do HD44780
        
        self.i2c = i2c
        self.i2c_addr = i2c_addr

        # Envia sinal neutro para garantir estabilidade no barramento
        self._write_byte(0x00)
        utime.sleep_ms(20)

        # Envia sequência de nibbles para reiniciar o LCD em modo 4 bits
        for _ in range(3):
            self._write_init_nibble(LCD_FUNCTION_RESET)
            utime.sleep_ms(5 if _ == 0 else 1)

        # Define o modo de operação do LCD
        self._write_init_nibble(LCD_FUNCTION)
        utime.sleep_ms(1)

        # Chama o construtor da classe base LcdApi
        super().__init__(num_lines, num_columns)

        # Configura modo de linhas (duas linhas se houver)
        cmd = LCD_FUNCTION
        if num_lines > 1:
            cmd |= LCD_FUNCTION_2LINES
        self.hal_write_command(cmd)

        gc.collect()  # Limpa memória após inicialização

    def hal_write_command(self, cmd: int):
        # Envia comando para o LCD via I2C
        self._send(cmd, is_data=False)
        if cmd <= 3:  # Comandos que exigem delay maior (clear, home...)
            utime.sleep_ms(5)
        gc.collect()

    def hal_write_data(self, data: int):
        # Envia dados (caracteres) para o LCD via I2C
        self._send(data, is_data=True)
        gc.collect()

    def hal_backlight_on(self):
        # Liga a luz de fundo do display
        self._write_byte(1 << SHIFT_BACKLIGHT)

    def hal_backlight_off(self):
        # Desliga a luz de fundo do display
        self._write_byte(0x00)

    def hal_sleep_us(self, usecs: int):
        # Pausa a execução por microssegundos (usado para sincronizar dados)
        utime.sleep_us(usecs)

    def _write_byte(self, byte: int):
        # Envia um byte direto para o módulo PCF8574 via I2C
        self.i2c.writeto(self.i2c_addr, bytes([byte]))

    def _write_init_nibble(self, nibble: int):
        # Envia um nibble de inicialização (4 bits) para o LCD
        data = ((nibble >> 4) & 0x0F) << SHIFT_DATA
        self._pulse(data)

    def _send(self, value: int, is_data: bool):
        # Prepara e envia os nibbles superiores e inferiores de um byte para o LCD
        rs = MASK_RS if is_data else 0x00  # Define se é dado ou comando
        bl = self.backlight << SHIFT_BACKLIGHT  # Define estado da luz de fundo
        high = ((value >> 4) & 0x0F) << SHIFT_DATA  # Nibble alto
        low  = (value & 0x0F) << SHIFT_DATA         # Nibble baixo

        self._pulse(rs | bl | high)  # Envia parte alta
        self._pulse(rs | bl | low)   # Envia parte baixa

    def _pulse(self, data: int):
        # Envia um pulso para confirmar envio de dado/comando
        self._write_byte(data | MASK_E)  # Enable alto
        self._write_byte(data)           # Enable baixo