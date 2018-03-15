#################################
## logging Utils
#################################
import logging
import sys
import time

LOG_NAME = "rainbowraceway"
def setup_logging(log_level=logging.INFO, logToFile=False):
    LOG_FILENAME = "./Logs/rainbowraceway"
    NAME = "rainbowraceway"
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(NAME)
    logger.setLevel(log_level)
    logger.addHandler(handler)

    if logToFile:
        handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=16000000, backupCount=5)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

def getLogger():
    return logging.getLogger(LOG_NAME)
#################################
## Async Utils
#################################
import asyncio
async def callLater(func,t):
    await asyncio.sleep(t)
    func()

async def async_cancel(cancelToken, t):
    await asyncio.sleep(t)
    cancelToken.cancel()

class CancelToken:
    def __init__(self, loop,parentToken=None):
        self.loop = loop
        self._future = loop.create_future()

    def isCancelled(self):
        return self._future.done()

    def cancel(self):
        #Discard Action if cancelToken is already cancelled
        if self._future.done():
            return

        self._future.set_result(True)

#################################
## LED Utils
#################################

import platform
import logging

if platform.system() != "Windows":
    from neopixel import *
else:
    logging.getLogger('root').warning("Windows OS: Detected. Using Stub NeoPixel Library --Light strips will not work")

    class ws:
        WS2811_STRIP_GRB = 0

    def Color(r, g, b, w=0):
        return (w << 24) | (r << 16) | (g << 8) | b


    class Adafruit_NeoPixel(object):
        def __init__(self, num, pin, freq_hz=800000, dma=5, invert=False,brightness=255, channel=0, strip_type=ws.WS2811_STRIP_GRB):
            self.num = num

        def __del__(self):
            pass

        def _cleanup(self):
            pass

        def begin(self):
            pass

        def show(self):
            pass

        def setPixelColor(self, n, color):
            pass

        def setPixelColorRGB(self, n, red, green, blue, white=0):
            pass

        def setBrightness(self, brightness):
            pass

        def getPixels(self):
            pass

        def numPixels(self):
            return self.num

        def getPixelColor(self, n):
            return 0

def create_and_init_neopixels(LED_COUNT=174, LED_PIN=18, LED_FREQ_HZ=800000, LED_DMA=5, LED_INVERT=False, LED_BRIGHTNESS=255, LED_CHANNEL=0,
                              LED_STRIP=ws.WS2811_STRIP_GRB):

    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL,LED_STRIP)
    strip.begin()

    for i in range(strip.numPixels()):
        strip.setPixelColor(i,0)
        strip.show()
    return strip


#################################
## SPI Utils
#################################

if platform.system() != "Windows":
    from spidev import SpiDev
else:
    logging.getLogger('root').warning("Windows OS: Detected. Using Stub SpiDev Library --Throttle will not work")

    class SpiDev():
        max_speed_hz = 0
        def open(self,a,b):
            pass

        def xfer(self,a):
            pass

def create_SpiDev():
    return SpiDev()

#################################
## ThrottleControl
#################################

def closeTo(a,b):
    closeToWithin(sys.float_info.epsilon)

def closeToWithin(a,b,v):
    return abs(a-b) < abs(v)


#################################
## Color Utils
#################################
import colorsys
def color2Hsv(color):
    w = (color & 0xFF000000)
    r = (color & 0x00FF0000)
    g = (color & 0x0000FF00)
    b = (color & 0x000000FF)

    if w:
        logging.getLogger(__name__).warning("W component conversion not implemented")
    return colorsys.rgb_to_hsv(r,g,b)

def hsv2Color(h,s,v):
    return Color(*map(lambda x: int(x*255),colorsys.hsv_to_rgb(h,s,v)))
