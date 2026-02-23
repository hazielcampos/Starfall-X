import serial
from utils.Config import get_config
from multiprocessing import Queue
import struct
import time
import queue
from utils.RobotEnums import Msg
from utils.Logger import Logger
from colorama import Fore

def CommNode(messages_queue: Queue, stop_event):   
    log = Logger("COMMS", Fore.YELLOW)
    port = get_config()["serial"]["port"]
    baudrate = get_config()["serial"]["baudrate"]
    timeout = get_config()["serial"]["timeout"]

    ser = None
    try:
        while not stop_event.is_set():
            if ser is None or not ser.is_open:
                try: 
                    log.Info(f"Trying to connect to port {port}...")
                    ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
                    time.sleep(2)
                    log.Info("Connection successful.")
                except serial.SerialException as e:
                    log.Error(f"Can't connect the the port: {e}")
                    time.sleep(2)
                    continue

            try:
                cmd, value = messages_queue.get(timeout=1)
                send_command(ser, cmd, value)
            
            except queue.Empty:
                continue
            except Exception as e:
                log.Error(f"Error processing the message: {e}")
    except KeyboardInterrupt:
                pass
    except Exception as e:
        log.Error(f"Unexpected error: {e}")
    finally:
        if ser and ser.is_open:
            send_command(ser, Msg.DIRECTION, 0)
            send_command(ser, Msg.DIRECTION, 0)
            ser.close()



def send_command(ser: serial.Serial, cmd, value):
    packet = struct.pack('<Bh', cmd, value)
    ser.write(packet)
    return packet