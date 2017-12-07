import inspect
import asyncio
import janus
import random
import platform
import serial
import serial.aio

import admin_behaviours
import dynamic_types
from introspect import getAssociatedObjects,verifyObjAssociationSanity
import race_behaviours
from rfid_reader import TagStream,RfidReader
from tags import admin_tags, race_tags
from utils import async_cancel, CancelToken
from utils import create_and_init_neopixels, create_SpiDev
from utils import setup_logging, logging, getLogger
from utils import closeTo

setup_logging(logging.DEBUG)
LOG_TAG = "core"

verifyObjAssociationSanity(admin_behaviours)
verifyObjAssociationSanity(race_behaviours)

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

class RaceController:
    def __init__(self, loop, trikeCtx,ct):

        self.loop = loop
        self.trikeCtx = trikeCtx

        self.createActionMap()

        self.subTask = loop.create_future()
        self.subTask.cancel()

        self.defaultTask = race_behaviours.DefaultBehaviour()
        self.launchDefaultTask()

    def createActionMap(self):
        self.actionMap = {}

        for associationObj in getAssociatedObjects(race_behaviours):
            self.actionMap[dynamic_types.typeFromString(associationObj.association)] = associationObj.obj

    def launchDefaultTask(self):
        self.defaultTask.launch(self.loop, self.trikeCtx)

    async def async_launchOneshotTask(self, state):
        self.defaultTask.cancel()
        await state.launch(self.loop,self.trikeCtx)
        self.launchDefaultTask()

    def onTag(self,tag):
        if not self.subTask.done():
            getLogger().getChild(LOG_TAG).info("TagOcclusion: Tag detected, but current Behaviour not finished")
            return

        if tag not in race_tags:
            getLogger().getChild(LOG_TAG).info("UnknownTag: New Tag detected, but Type is not Specified - Tag:%s"%(tag))
            return

        actionType = race_tags[tag]
        if actionType not in self.actionMap:
            getLogger().getChild(LOG_TAG).error("ProgramingError: No behaviour specified for '%s' " %(actionType))
            return

        self.subTask = self.loop.create_task(
            self.async_launchOneshotTask(self.actionMap[actionType]())
        )

class AdminController:

    def __init__(self,loop,cancelToken,trikeCtx):
        self.loop = loop
        self.cancelToken = cancelToken
        self.trikeCtx = trikeCtx
        self.subController = None
        self.createActionMap()

    def createActionMap(self):
        self.actionMap = {}
        for associationObj in getAssociatedObjects(admin_behaviours):
            self.actionMap[dynamic_types.typeFromString(associationObj.association)] = associationObj.obj

    def onStartup(self):
        self.subController = RaceController(self.loop, self.trikeCtx, self.cancelToken)

    def onTag(self,tag):
        getLogger().getChild(LOG_TAG).info("AdminTag RECV - Tag:%s" % (tag))
        self.actionMap[admin_tags[tag]](self,self.trikeCtx)

    def createTask(self, loop, tagSource):
        self.onStartup()
        return loop.create_task(self.async_tagProcessor(tagSource))

    async def async_tagProcessor(self, tagGenerator):
        async for tag in tagGenerator:
            if tag in admin_tags:
                self.onTag(tag)
            else:
                self.subController.onTag(tag)


if __name__ == "__main__":

    trikeCtx = TrikeCtx.createProductionCtx()
    loop = asyncio.get_event_loop()
    cancelToken = CancelToken(loop)

    queue = janus.Queue(loop=loop)
    taskController = AdminController(loop, cancelToken, trikeCtx)
    tagStream = TagStream(queue.async_q)
    tasks = []

    tasks.append(serial.aio.create_serial_connection(loop, lambda: RfidReader(queue.sync_q), '/dev/ttyUSB0', baudrate=115200))
    tasks.append(taskController.createTask(loop, tagStream))
    tasks.append(loop.create_task(async_cancel(cancelToken, 20)))
    loop.run_until_complete(asyncio.gather(*tasks))

