import inspect
import asyncio
import janus
import random
import serial
import serial.aio

from behaviours import *
from rfid_reader import TagStream,RfidReader
from tags import *
from utils import async_cancel, CancelToken
from utils import create_and_init_neopixels
from utils import setup_logging, logging, getLogger


setup_logging(logging.DEBUG)
LOG_TAG = "core"

class RaceController:
    def __init__(self, loop, ledStrip,ct):

        self.loop = loop
        self.ledStrip = ledStrip

        self.subTask = loop.create_future()
        self.subTask.cancel()

        self.defaultTask = DefaultBehaviour()
        self.launchDefaultTask()

        self.tagTaskMap = {
            TagType.POWERUP1: ExamplePowerup,
            TagType.POWERUP2: OtherExamplePowerup,
        }

    def launchDefaultTask(self):
        self.defaultTask.launch(self.loop, self.ledStrip)

    async def async_launchOneshotTask(self, state):
        self.defaultTask.cancel()
        await state.launch(self.loop,self.ledStrip)
        self.launchDefaultTask()

    def onTag(self,tag):
        if not self.subTask.done():
            getLogger().getChild(LOG_TAG).info("TagOcclusion: Tag detected, but current Behaviour not finished")
            return

        if tag not in TagTypeMap_Powerup:
            getLogger().getChild(LOG_TAG).info("UnknownTag: New Tag detected, but Type is not Specified - Tag:%s"%(tag))
            return

        tagType = TagTypeMap_Powerup[tag]

        if tagType not in self.tagTaskMap:
            getLogger().getChild(LOG_TAG).error("ProgramingError: No behaviour specified for '%s' in tagTypeMap" %(tagType))
            return

        self.subTask = self.loop.create_task(
            self.async_launchOneshotTask(self.tagTaskMap[tagType]())
        )


class AdminController:

    def __init__(self,loop,cancelToken):
        self.loop = loop
        self.cancelToken = cancelToken;
        self.subController = None

    def onStartup(self):
        ledStrip = create_and_init_neopixels()
        self.subController = RaceController(self.loop, ledStrip, self.cancelToken)

    def onTag(self,tag):
        getLogger().getChild(LOG_TAG).info("AdminTag RECV - Tag:%s" % (tag))

    def createTask(self, loop, tagSource):
        self.onStartup()
        return loop.create_task(self.async_tagProcessor(tagSource))

    async def async_tagProcessor(self, tagGenerator):
        async for tag in tagGenerator:
            if tag in TagTypeMap_Admin:
                self.onTag(tag)
            else:
                self.subController.onTag(tag)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    cancelToken = CancelToken(loop)

    queue = janus.Queue(loop=loop);
    taskController = AdminController(loop, cancelToken)
    tagStream = TagStream(queue.async_q)
    tasks = []

    tasks.append(serial.aio.create_serial_connection(loop, lambda: RfidReader(queue.sync_q), '/dev/ttyUSB0', baudrate=115200))
    tasks.append(taskController.createTask(loop, tagStream))
    tasks.append(loop.create_task(async_cancel(cancelToken, 20)))
    loop.run_until_complete(asyncio.gather(*tasks))

