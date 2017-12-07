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
from utils import setup_logging, logging, getLogger

setup_logging(logging.DEBUG)
LOG_TAG = "core"

verifyObjAssociationSanity(admin_behaviours)
verifyObjAssociationSanity(race_behaviours)


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
    from trike_ctx import TrikeCtx

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

