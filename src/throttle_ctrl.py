import asyncio
from utils import closeTo,create_SpiDev, getLogger
LOG_TAG = "ThrottleCtl"
class ThrottleCtrl:

    def __init__(self):
        self.init_spi()
        self.currThrottle = 0
        self.maxThrottle= 1  # % of total power (0 - 1 range) determined by powerup
        self.baseThrottle = 0.2  # % of total power (0 - 1 range) determined by the race mode
        self.deltaT = 0.1


    def init_spi(self):
        self.spi = create_SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 10000

    def _write_pot(self,input):
        msb = input >> 8
        lsb = input & 0xFF
        resp = self.spi.xfer([msb, lsb])

    # Sets the maximum throttle between 0 and 1 (0-100%)
    def configureMaxThrottle(self,throttle):
        assert (0 <= throttle <= 1)
        self.maxThrottle = throttle
        getLogger().getChild(LOG_TAG).info("SetMaxThrottle(%f)" % (throttle))

    def configureBaseThrottle(self,throttle):
        assert( 0 <= throttle <= 1)
        self.baseThrottle = throttle
        self.currThrottle = throttle
        getLogger().getChild(LOG_TAG).info("SetBaseThrottle(%f)" % (throttle))
        self._write_pot(int(throttle * 255))

    def setThrottle(self,val):
        self.currThrottle = val
        self._write_pot(val)

    async def lerpThrottle(self,powerValue,totalDuration):
        distance = (powerValue - self.currThrottle)
        stepSize = distance / ((float(totalDuration) / self.deltaT))
        asyncio.sleep(0)
        while not closeTo(self.currThrottle, powerValue):
            await asyncio.sleep(self.deltaT)
            self.setThrottle(self.currThrottle + stepSize)
        self.currThrottle = powerValue

class MockThrottleCtrl(ThrottleCtrl):

    def __init__(self):
        self.init_spi()
        self.currThrottle = 0
        self.maxThrottle= 1  # % of total power (0 - 1 range) determined by powerup
        self.baseThrottle = 0.2  # % of total power (0 - 1 range) determined by the race mode
        self.deltaT = 0.1

    def init_spi(self):
        pass

    def _write_pot(self,input):
        getLogger().getChild(LOG_TAG).info("Writing to Spi(%B)" % (input))
