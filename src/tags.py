from enum import Enum

class TagType(Enum):
    ADMIN1 = 0
    POWERUP1 = 100
    POWERUP2 = 101


TagTypeMap_Admin = {
    "AFF345D3": TagType.ADMIN1
}

TagTypeMap_Powerup = {
    "005180000c0076129092bf": TagType.POWERUP1,
    "84D31AF3": TagType.POWERUP2
}
