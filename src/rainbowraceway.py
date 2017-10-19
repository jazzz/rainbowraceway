import inspect
import asyncio
import random
from enum import Enum
from utils import create_and_init_neopixels, setup_logging, logging,getLogger, async_cancel
from behaviours import *


setup_logging(logging.DEBUG)
LOG_TAG = "core"

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

class TagType(Enum):
    ADMIN_TASK = 0
    POWERUP1 = 1
    POWERUP2 = 2


tagTypeMap = {
    "AFF345D3": TagType.ADMIN_TASK,
    "54D31AF2": TagType.POWERUP1,
    "84D31AF3": TagType.POWERUP2
}




class TaskController:
    def __init__(self, loop, ledStrip,ct):

        self.loop = loop
        self.rootCt = ct
        self.ledStrip = ledStrip

        self.subTask = loop.create_future()
        self.subTask.cancel()

        self.dt = DefaultBehaviour()
        self.dt.launch(loop,self.ledStrip)

        self.tagTaskMap = {
            #TagType.ADMIN_TASK: self.async_onCoinsAdded,
            TagType.POWERUP1: ExamplePowerup,
            TagType.POWERUP2: OtherExamplePowerup,
        }

    def createTask(self, loop, tagSource):
        return loop.create_task(self.async_tagProcessor(tagSource))

    async def async_launchOneshotTask(self, state):

        self.dt.cancel()

        state.launch(self.loop,self.ledStrip)
        await state.task()

        self.dt.launch(self.loop,self.ledStrip)

    @asyncio.coroutine
    async def async_tagProcessor(self, tagGenerator):
        async for tag in tagGenerator:

            if not self.subTask.done():
                getLogger().getChild(LOG_TAG).info(
                    "TagOcclusion: Tag detected, but current Behaviour not finished"
                )
                continue

            if tag not in tagTypeMap:
                getLogger().getChild(LOG_TAG).info(
                    "UnknownTag: New Tag detected, but Type is not Specified - Tag:%s"%(tag)
                )
                continue

            tagType = tagTypeMap[tag]

            if tagType not in self.tagTaskMap:
                getLogger().getChild(LOG_TAG).error("ProgramingError: No behaviour specified for '%s' in tagTypeMap" %(tagType))
                continue

            self.subTask = self.loop.create_task(
                self.async_launchOneshotTask(self.tagTaskMap[tagType]())
            )

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    cancelToken = CancelToken(loop)

    ledStrip = create_and_init_neopixels()
    taskController = TaskController(loop, ledStrip,cancelToken)

    tasks = []

    tasks.append(taskController.createTask(loop, MockTagReader(cancelToken, 5)))
    tasks.append(loop.create_task(async_cancel(cancelToken, 20)))
    return_value = loop.run_until_complete(asyncio.gather(*tasks))

