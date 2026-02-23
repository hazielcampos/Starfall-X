import cv2
import queue
from multiprocessing import Queue
from utils.RobotEnums import RobotState
import time
from utils.Logger import Logger
from colorama import Fore


# Change from cv2.VideoCapture to "picamera2"
# Clamp exposure, white balance and gain

def CameraNode(frame_queue: Queue, state_queue: Queue, stop_event):

    video = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    frame_time = 1/30
    last_state = RobotState.IDLE
    log = Logger("CAMERA", Fore.GREEN)
    try:
        while not stop_event.is_set():
            if video is None or not video.isOpened():
                video = cv2.VideoCapture(0, cv2.CAP_V4L2)
                video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                log.Error("Video can't be opened. Waiting 3 seconds and trying again.")
                time.sleep(3)
                continue

            start_time = time.time()

            # Check state without blocking
            try:
                last_state = state_queue.get_nowait()
                if last_state in (RobotState.TERMINATED, RobotState.ERROR):
                    break
            except queue.Empty:
                pass

            ret, frame = video.read()
            if not ret:
                log.Error("Can't read frame.")
                break
            # Avoid blocking if the queue is full
            try:
                frame_queue.put_nowait(frame)
            except queue.Full:
                try:
                    frame_queue.get_nowait()
                except queue.Empty:
                    pass
                frame_queue.put_nowait(frame)

            elapsed = time.time() - start_time
            if elapsed < frame_time:
                time.sleep(frame_time - elapsed)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        log.Error(f"Unexpected error: {e}")

    finally:
        video.release()
        cv2.destroyAllWindows()
