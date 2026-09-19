import gpiozero as GPIO
import time

pina = GPIO.output_device(2)
pinb = GPIO.output_device(3)
def main():
    pina.off()
    pinb.off()
    time.sleep(60)

if __name__ == "__main__":
    main()