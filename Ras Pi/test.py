import gpiozero as GPIO
import time

pina = GPIO.OutputDevice(2)
pinb = GPIO.OutputDevice(3)
def main():
    pina.off()
    pinb.off()
    time.sleep(15)
    pina.on()
    pinb.on()
    time.sleep(15)

if __name__ == "__main__":
    while True:
        main()