from zapper import Zapper, TerminalAllocator

zapper = Zapper()
terminal_allocoator = TerminalAllocator()

def calculate_zap_duration(damage, total_sustained_damage):
    #can be used to create a scaling hurt factor
    #stubbed for now
    return 1.0
class Player:
    def __init__(self, username:str):
        self.username:str = username
        self.terminal:str = terminal_allocoator.get_terminal()
        self.in_play:bool = False
        self.has_terminal:bool = False
        if self.terminal != "tX":
            self.has_terminal = True
        self.sustained_damage:float = 0.0
        self.total_large_zaps = 0
        self.total_small_zaps = 0
        print(f"{username} is using pins Terminal {self.terminal}")
    
    
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


if __name__ == "__main__":
    print("Hello World, I am a Zapper")