import cv2
import queue
from multiprocessing import Queue
from utils.RobotEnums import RobotState
import time

def VideoProcessingNode(frame_queue: Queue, video_results_queue: Queue, overlays_queue: Queue, stop_event):
    pass