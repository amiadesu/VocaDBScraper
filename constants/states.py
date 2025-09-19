from enum import Enum

class ResponseState(Enum):
    UNKNOWN = 0
    SUCCESS = 1
    DELETED = 2
    NOT_FOUND = 3