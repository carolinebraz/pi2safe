import utime
from lcd_display import startup_message
from security import SecurityManager

def main():
    startup_message()

    security_manager = SecurityManager()
    security_manager.setup_initial()

    while True:
        guess = security_manager.input_code()
        security_manager.check_pin(guess)
        
        utime.sleep(0.5)

if __name__ == "__main__":
    main()