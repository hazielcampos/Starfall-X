from colorama import Fore, init

class Logger:
    def __init__(self, module_name, color):
        self.module_name = module_name
        self.color = color
    
    def Warn(self, msg):
        print(f"{self.color}[{self.module_name}] {Fore.YELLOW}[WARN] {msg}")
    
    def Error(self, msg):
        print(f"{self.color}[{self.module_name}] {Fore.RED}[ERROR] {msg}")
    
    def Info(self, msg):
        print(f"{self.color}[{self.module_name}] {Fore.CYAN}[INFO] {msg}")

    def Print(self, msg):
        print(f"{self.color}[{self.module_name}] {Fore.GREEN}[LOG] {msg}")