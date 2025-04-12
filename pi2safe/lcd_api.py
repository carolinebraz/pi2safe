# Adaptado do repositório dhylands/python_lcd por Dave Hylands
# Fonte original: https://github.com/dhylands/python_lcd
# Esta classe define a API genérica para displays HD44780
# O envio físico dos dados (via I2C, GPIO, etc.) deve ser implementado por uma classe derivada

import time  # Usado para temporização em microssegundos

# Conjunto de comandos do controlador HD44780 — todos representados como máscaras de bits
LCD_CLR             = 0x01      # Limpa o display
LCD_HOME            = 0x02      # Retorna o cursor para a posição inicial

LCD_ENTRY_MODE      = 0x04      # Modo de entrada de texto
LCD_ENTRY_INC       = 0x02      # Avança cursor após escrever
LCD_ENTRY_SHIFT     = 0x01      # Deslocamento do display

LCD_ON_CTRL         = 0x08      # Controle de exibição
LCD_ON_DISPLAY      = 0x04      # Ativa exibição
LCD_ON_CURSOR       = 0x02      # Ativa cursor
LCD_ON_BLINK        = 0x01      # Pisca cursor

LCD_MOVE            = 0x10      # Movimentação de cursor/display
LCD_MOVE_DISP       = 0x08      # Move display
LCD_MOVE_RIGHT      = 0x04      # Move para a direita

LCD_FUNCTION        = 0x20      # Configuração de função
LCD_FUNCTION_8BIT   = 0x10      # Modo 8 bits
LCD_FUNCTION_2LINES = 0x08      # Duas linhas
LCD_FUNCTION_10DOTS = 0x04      # Fonte 5x10
LCD_FUNCTION_RESET  = 0x30      # Inicialização especial

LCD_CGRAM           = 0x40      # Endereço da CGRAM (caracteres personalizados)
LCD_DDRAM           = 0x80      # Endereço da DDRAM (posições do display)

class LcdApi:
    # Classe abstrata: define comandos e controle de cursor, mas não a comunicação física

    def __init__(self, num_lines, num_columns):
        self.num_lines = min(num_lines, 4)       # LCDs de até 4 linhas
        self.num_columns = min(num_columns, 40)  # Até 40 colunas
        self.cursor_x = 0
        self.cursor_y = 0
        self.implied_newline = False
        self._backlight = True  # Estado da luz de fundo

        self.display_off()
        self.backlight = True
        self.clear()
        self.hal_write_command(LCD_ENTRY_MODE | LCD_ENTRY_INC)
        self.hide_cursor()
        self.display_on()

    @property
    def backlight(self):
        return self._backlight

    @backlight.setter
    def backlight(self, value):
        self._backlight = value
        if value:
            self.hal_backlight_on()
        else:
            self.hal_backlight_off()

    def clear(self):
        # Limpa display e reposiciona cursor
        self.hal_write_command(LCD_CLR)
        self.hal_write_command(LCD_HOME)
        self.cursor_x = 0
        self.cursor_y = 0

    def show_cursor(self):
        # Exibe cursor visível
        self.hal_write_command(LCD_ON_CTRL | LCD_ON_DISPLAY | LCD_ON_CURSOR)

    def hide_cursor(self):
        # Esconde cursor
        self.hal_write_command(LCD_ON_CTRL | LCD_ON_DISPLAY)

    def blink_cursor_on(self):
        # Ativa cursor piscante
        self.hal_write_command(LCD_ON_CTRL | LCD_ON_DISPLAY | LCD_ON_CURSOR | LCD_ON_BLINK)

    def blink_cursor_off(self):
        # Cursor sólido, sem piscar
        self.hal_write_command(LCD_ON_CTRL | LCD_ON_DISPLAY | LCD_ON_CURSOR)

    def display_on(self):
        # Ativa exibição
        self.hal_write_command(LCD_ON_CTRL | LCD_ON_DISPLAY)

    def display_off(self):
        # Desativa exibição (sem apagar conteúdo)
        self.hal_write_command(LCD_ON_CTRL)

    def move_to(self, cursor_x, cursor_y):
        # Move cursor para posição (coluna, linha)
        self.cursor_x = cursor_x
        self.cursor_y = cursor_y
        addr = cursor_x & 0x3F
        if cursor_y & 1:
            addr += 0x40
        if cursor_y & 2:
            addr += self.num_columns
        self.hal_write_command(LCD_DDRAM | addr)

    def putchar(self, char):
        # Escreve um único caractere na posição atual e avança o cursor
        if char == '\n':
            if not self.implied_newline:
                self.cursor_x = self.num_columns
        else:
            self.hal_write_data(ord(char))
            self.cursor_x += 1

        if self.cursor_x >= self.num_columns:
            self.cursor_x = 0
            self.cursor_y += 1
            self.implied_newline = (char != '\n')

        if self.cursor_y >= self.num_lines:
            self.cursor_y = 0

        self.move_to(self.cursor_x, self.cursor_y)

    def putstr(self, string):
        # Escreve uma string inteira no display, caractere por caractere
        for char in string:
            self.putchar(char)

    def custom_char(self, location, charmap):
        # Cria caractere personalizado (até 8 disponíveis)
        location &= 0x7
        self.hal_write_command(LCD_CGRAM | (location << 3))
        for i in range(8):
            self.hal_write_data(charmap[i])
            self.hal_sleep_us(40)
        self.move_to(self.cursor_x, self.cursor_y)

    # Métodos hal – Devem ser implementados por subclasses específicas
    def hal_backlight_on(self): pass
    def hal_backlight_off(self): pass
    def hal_write_command(self, cmd): raise NotImplementedError
    def hal_write_data(self, data): raise NotImplementedError

    def hal_sleep_us(self, usecs):
        # Temporização em microssegundos
        time.sleep_us(usecs)