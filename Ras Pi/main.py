from zapper import Relay
from time import sleep
import yaml
zapper = Zapper()
terminal_allocoator = TerminalAllocator()

global_queue = []



def calculate_zap_duration(damage, total_sustained_damage):
    #can be used to create a scaling hurt factor
    #stubbed for now
    return 1.0

def get_relay(username):
    players = {
        "test":(0,1),
        "test2":(2,3)
    }
    
    gpio_pins = players.get(username, (13,14))
    relay = Relay(gpio_pins)
    return relay


class Player:
    def __init__(self, username:str):
        self.username:str = username
        self.relay = get_relay(username)
    
    def take_damage(self, damage:float):
        duration = calculate_zap_duration(damage, self.sustained_damage)
        self.sustained_damage += damage
        
        if damage >= 5.0:
            self.request_large_zap(duration)
        else:
            self.request_small_zap(duration)

    def request_large_zap(self, duration):
        self.total_large_zaps +=1
        zapper.queue_large_zap(self.terminal, duration, self.username)
    
    def request_small_zap(self, duration):
        self.total_small_zaps +=1
        zapper.queue_small_zap(self.terminal, duration, self.username)



def create_players():
    with open("config.yaml") as stream:
        try:
            player_config = yaml.safe_load(stream)
        except Exception as e:
            print(e)
    
    
    
def temp_test():
    test_player = Player("test_player")
    
    
    while True:
        test_player.take_damage(5.5)
        
        sleep(2)
        
        test_player. take_damage(1)
    

def recive_webhook(webhook):
    player_name = webhook.get("name")
    damage = webhook.get("damage")
    
    

if __name__ == "__main__":
    print("Hello World, I am a Zapper")
    
    temp_test()