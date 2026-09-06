from time import sleep
import gpiozero as GPIO


relay_pulse_seconds = 0.2
MAX_DURATION = 2.0

terminals: dict[str, list[tuple[int, int]]] = {
    "t1": [(0, 1), (2, 3)],
    "t2": [(4, 5), (6, 7)],
    "t3": [(8, 9), (10, 11)],
    "t4": [(12, 13), (14, 15)],
    "t5": [(16, 17), (18, 19)],
    "t6": [(20, 21), (22, 23)],
    "tX": [(24, 25), (24, 25)]
}


class Relay:

    def __init__(self, pins):
        pin_a, pin_b = pins
        self.a = GPIO.DigitalOutputDevice(pin_a, initial_value=False)
        self.b = GPIO.DigitalOutputDevice(pin_b, initial_value=False)
        self.pulse_seconds = relay_pulse_seconds

    def coil_off(self):
        self.a.off()
        self.b.off()

    def drive_switch_off(self):
        self.coil_off()
        self.a.off()
        self.b.on()
        sleep(self.pulse_seconds)
        self.coil_off()

    def drive_switch_on(self):
        self.coil_off()
        self.b.off()
        self.a.on()
        sleep(self.pulse_seconds)
        self.coil_off()


class Zapper:

    def __init__(self):
        self.pins = []
        self.output_termnials = self.create_output_termnials()
        self.large_zap_queue = []
        self.small_zap_queue = []

    def create_output_termnials(self):
        output_termnials = {}
        for termnial_name, (large_pins, small_pins) in terminals.items():
            output_termnials[termnial_name] = (Relay(large_pins), Relay(small_pins))
        return output_termnials

    def reset_all(self):
        for _, (large_relay, small_relay) in self.output_termnials.items():
            large_relay.drive_switch_off()
            small_relay.drive_switch_off()

    def apply_zap(self, relay: Relay, duration: float):
        if duration > MAX_DURATION:
            duration = 0.5

        relay.drive_switch_on()
        sleep(duration)
        relay.drive_switch_off()

        self.reset_all()

        return 1
    
    def apply_large_zap(self):
        zap_obj = self.large_zap_queue[0]
        duration = zap_obj[1]
        player_name = zap_obj[3]
        relay = self.output_termnials[zap_obj[0]]
        
        result = self.apply_zap(relay, duration)
        
        if result == 1:
            print(f"Large Zap applied for {player_name}")
        
        self.large_zap_queue.pop(0)
        if len(self.large_zap_queue) > 0:
            self.apply_large_zap()

        
    def apply_small_zap(self):
            zap_obj = self.large_zap_queue[0]
            duration = zap_obj[1]
            player_name = zap_obj[3]
            relay = self.output_termnials[zap_obj[1]]
            
            result = self.apply_zap(relay, duration)
            
            if result == 1:
                print(f"Large Zap applied for {player_name}")
            
            self.small_zap_queue.pop(0)
            if len(self.small_zap_queue) >0:
                self.apply_small_zap()

    def queue_large_zap(self,terminal_name:str, duration:float, player_name:str):
        
        self.large_zap_queue.append((terminal_name, duration, player_name))
        
        print(f"Large Zap Queued for {player_name}")
        self.apply_large_zap()


    def queue_small_zap(self, terminal_name: str, duration: float, player_name:str):
        self.small_zap_queue.append((terminal_name, duration, player_name))
        
        print(f"Small Zap Queued for {player_name}")
        self.apply_small_zap()


class TerminalAllocator:
    def __init__(self, max_pins: int = 24) -> None:
        self.max_pins = max_pins
        self.used_terminals: list[str] = []

    def get_terminal(self) -> str:
        terminal: str = "tX"

        if len(self.used_terminals) >= len(terminals):
            print("Not Enough Terminals for all Players")
            return terminal

        for t in terminals:
            if t not in self.used_terminals:
                terminal = t
                break

        return terminal

