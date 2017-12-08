import asyncio
from utils import closeToWithin,create_SpiDev, getLogger
LOG_TAG = "ThrottleCtl"

class ThrottleCtrl:
    """
    Configures the digital pot to control throttle values. A Base Throttle is set as a reference point
    and then a power ratio is used to control throttle values based on that reference point.

    eg. 1.2 would be a 20% increase in power

    You may ask for 200% power but the motor might not be able to
    provide that, but it will try its best.
    """
    BASE_RATIO = 1.0

    def __init__(self):
        self.init_spi()
        self.__baseThrottle = 0.5   # range (0,1] this establishes the normal (non-powerup) reference point
        self.__deltaT = 0.03        # Euler step resolution in seconds

        self.__currentPowerRatio = 1.0    # nominal range(0,2). expresses current power as a ratio of the
                                        # refrence point.

    def init_spi(self):
        self.spi = create_SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 10000

    def __write_pot(self,input):
        msb = input >> 8
        lsb = input & 0xFF
        resp = self.spi.xfer([msb, lsb])

    def __setThrottle(self,t):
        t = max(0.001,min(t,1))
        self.__write_pot(int(t * 255))

    def configureBaseThrottle(self,throttle):
        assert( 0 <= throttle <= 1)
        self.__baseThrottle = throttle
        getLogger().getChild(LOG_TAG).info("SetBaseThrottle(%f)" % (throttle))
        self.__setThrottle(throttle)

    def setPowerRatio(self,powerRatio):
        self.__currentPowerRatio = powerRatio
        self.__setThrottle(self.__baseThrottle*powerRatio)

    def currentPowerRatio(self):
        return self.__currentPowerRatio

    def resetThrottle(self):
        self.__setThrottle(self.__baseThrottle)

    #######################
    ## Helper Coroutines
    #######################

    async def lerpThrottle(self,dstPowerRatio,totalDuration):
        distance = dstPowerRatio - self.currentPowerRatio()
        stepSize = distance / ((float(totalDuration) / self.__deltaT))
        asyncio.sleep(0)
        while not closeToWithin(self.currentPowerRatio(), dstPowerRatio,stepSize):
            await asyncio.sleep(self.__deltaT)
            self.setPowerRatio(self.currentPowerRatio() + stepSize)
        self.setPowerRatio(dstPowerRatio)   #clamp rounding errors from euler steps

class MockThrottleCtrl(ThrottleCtrl):

    def __init__(self):
        self.init_spi()

    def init_spi(self):
        pass

    def _write_pot(self,input):
        getLogger().getChild(LOG_TAG).info("Writing to Spi(%B)" % (input))


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    t = ThrottleCtrl()
    tasks = []
    tasks.append(loop.create_task(t.lerpThrottle(0.5,2)))
    loop.run_until_complete(asyncio.gather(*tasks))