from enum import Enum

class Service(Enum):
    UNKNOWN = 0
    YOUTUBE = 1
    NICONICO = 2
    BILIBILI = 3

service_names_map = {
    Service.YOUTUBE: 'Youtube',
    Service.NICONICO: 'NicoNicoDouga',
    Service.BILIBILI: 'Bilibili'
}