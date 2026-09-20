import gpiozero as GPIO
import time

pina = GPIO.OutputDevice(2)
pinb = GPIO.OutputDevice(3)
pinc = GPIO.OutputDevice(4)
pind = GPIO.OutputDevice(5)
def main():
    pina.on()
    pinb.on()
    pinc.on()
    pind.on()
    print("off for 5")
    time.sleep(5)
    pina.off()
    pinb.off()
    print("player A on for 1.5")
    time.sleep(1.5)
    pina.on()
    pinb.on()
    pinc.on()
    pind.on()
    pinc.off()
    pind.off()
    time.sleep(1.5)
    print("player B on for 1.5")
    pina.on()
    pinb.on()
    pinc.on()
    pind.on()



if __name__ == "__main__":
    while True:
        main()