from enum import Enum, IntEnum

class RobotState(IntEnum):
    IDLE = 0
    TERMINATED = 1
    RUNNING = 2
    ERROR = 3

class Msg(IntEnum):
    DIRECTION = 0
    SPEED = 1