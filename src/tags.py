from enum import Enum

class TagType(Enum):
    ADMIN1 = 0
    POWERUP1 = 100
    POWERUP2 = 101


TagTypeMap_Admin = {
    "AFF345D3": TagType.ADMIN1
}

TagTypeMap_Powerup = {
    "54D31AF2": TagType.POWERUP1,
    "84D31AF3": TagType.POWERUP2
}
