from multiprocessing import Queue, Process, Event
import time
from utils.Messages import send_start_banner
from colorama import Fore, Style, init as colorInt
from utils.Logger import Logger

colorInt(autoreset=True)

from nodes.vision.camera import CameraNode
from nodes.comm.serial_node import CommNode
from nodes.control.driver_logic import ControlNode
from nodes.web.server import WebNode

if __name__ == "__main__":
    log = Logger("MAIN", Fore.WHITE)
    send_start_banner()
    time.sleep(0.3)

    log.Info("Starting system...")
    data_queue = Queue(maxsize=10)
    state_queue = Queue(maxsize=1)
    messages_queue = Queue(maxsize=20)
    stop_event = Event()

    nodes = {
        "camera": Process(target=CameraNode, args=(data_queue, state_queue, stop_event)),
        "comm": Process(target=CommNode, args=(messages_queue, stop_event)),
        "control": Process(target=ControlNode, args=(messages_queue, data_queue, stop_event)),
        "web": Process(target=WebNode, args=(data_queue, stop_event)),
    }

    for name, node in nodes.items():
        log.Info(f"Initializing the node: {name}.")
        node.start()

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        log.Info("Stopping...")
        stop_event.set()

        for node in nodes.values():
            node.join(timeout=3)

        for node in nodes.values():
            if node.is_alive():
                log.Warn(f"Force killing {node.name}")
                node.terminate()