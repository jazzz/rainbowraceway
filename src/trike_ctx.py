from throttle_ctrl import ThrottleCtrl,MockThrottleCtrl
from utils import create_and_init_neopixels, create_SpiDev

class TrikeCtx:
    def __init__(self,throttle,light):
        self.throttleCtrl =  throttle
        self.strip = light


    @staticmethod
    def createProductionCtx():
        return TrikeCtx(ThrottleCtrl(),create_and_init_neopixels())

    @staticmethod
    def createMockCtx():
        return TrikeCtx(MockThrottleCtrl(), create_and_init_neopixels())
    