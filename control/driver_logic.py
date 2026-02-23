from utils.Config import get_config
from multiprocessing import Queue
import time
import random
from utils.Logger import Logger
from colorama import Fore

def ControlNode(messages_queue: Queue, stop_event):
    log = Logger("CONTROL", Fore.BLUE)
    try:
        while not stop_event.is_set():
            angle = random.randint(-90, 90)
            info, error = send_command(messages_queue, 0, angle)
            if error:
                log.Error(f"Error sending command: {error}")
            time.sleep(5)
    except KeyboardInterrupt:
        pass
    
    except Exception as e:
        log.Error(f"Unexpected error: {e}")
    
    finally:
        log.Warn("Node finalized.")

def send_command(msg_queue: Queue, cmd, value):
    try:
        msg_queue.put_nowait((cmd, value))
        return "Command sent", None
    except Exception as e:
        return None, e
