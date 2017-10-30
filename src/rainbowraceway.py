import inspect
import asyncio
import random

from src.behaviours import *
from src.tags import *
from src.utils import async_cancel, CancelToken
from src.utils import create_and_init_neopixels
from src.utils import setup_logging, logging, getLogger


setup_logging(logging.DEBUG)
LOG_TAG = "core"

class MockTagReader:

    def __init__(self, cancelToken, delay):
        self.cancelToken = cancelToken
        self.delay = delay
        self.tagList = ["AFF345D3", "54D31AF2","84D31AF3","FFFFFFFF"]

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.cancelToken.isCancelled():
            raise StopAsyncIteration
        await asyncio.sleep(self.delay)
        return random.choice(self.tagList)

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
        self.defaultTask.launch(loop, self.ledStrip)

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
        self.subController = RaceController(loop, ledStrip, cancelToken)

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

    taskController = AdminController(loop, cancelToken)

    tasks = []

    tasks.append(taskController.createTask(loop, MockTagReader(cancelToken, 5)))
    tasks.append(loop.create_task(async_cancel(cancelToken, 20)))
    return_value = loop.run_until_complete(asyncio.gather(*tasks))

