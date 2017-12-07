import asyncio
from utils import callLater, Color,logging,getLogger
from introspect import Associate
LOG_TAG="race_behaviour"

class Behaviour:

    def __init__(self):
        self.__subtasks = []
        self.fps = 30
    def onEnter(self):
        pass

    def onExit(self):
        pass

    def onDraw(self):
        pass

    async def __taskLoop(self,ctx):
        self.ctx = ctx
        self.onEnter()
        try:
            await asyncio.sleep(0)
            while True:
                self.onDraw()
                await asyncio.sleep(float(1)/self.fps)
        except asyncio.CancelledError:
            pass

        self.cancelTasks()
        self.onExit()

    def launch(self,loop,ctx):

        self.loop = loop
        self.__task = loop.create_task(self.__taskLoop(ctx))
        return self.__task

    def task(self):
        return self.__task

    def cancel(self):
        self.__task.cancel()

    def launchSubtask(self,coro):
        self.__subtasks.append(self.loop.create_task(coro))

    def cancelTasks(self):
        for task in self.__subtasks:
            task.cancel()
        self.__task.cancel()

    def setFps(self,fps):
        self.fps = fps

class DefaultBehaviour(Behaviour):

    def onEnter(self):
        getLogger().getChild(LOG_TAG).debug("Enter %s"%(type(self).__name__))
        self.mode = 0
        self.setFps(10)

    def onExit(self):
        getLogger().getChild(LOG_TAG).debug("Exit %s" % (type(self).__name__))

    def onDraw(self):
        self.mode = 1-self.mode
        for i in range(self.ctx.strip.numPixels()):
            self.ctx.strip.setPixelColor(i,Color(self.mode*255,0,0))
        self.ctx.strip.show()

@Associate("banana")
class ExamplePowerup(Behaviour):
    index = 0
    def onEnter(self):
        getLogger().getChild(LOG_TAG).debug("Enter %s" % (type(self).__name__))
        self.color = Color(0,255,255)
        self.launchSubtask(callLater(self.cancel,5))
        self.launchSubtask(self.update())

    def onExit(self):
        getLogger().getChild(LOG_TAG).debug("Exit %s" % (type(self).__name__))

    def onDraw(self):
        for i in range(self.ctx.strip.numPixels()):
            c = 0
            if i == self.index:
                c = self.color
            self.ctx.strip.setPixelColor(i,c)
        self.ctx.strip.show()

    async def update(self):
        while True:
            await asyncio.sleep(0.1)
            self.index +=1
            self.index %= 4

@Associate("Green Shell")
class OtherExamplePowerup(Behaviour):
    index = 0
    def onEnter(self):
        getLogger().getChild(LOG_TAG).debug("Enter %s" % (type(self).__name__))
        self.color = Color(0,255,50)
        self.launchSubtask(callLater(self.cancel,5))
        self.launchSubtask(self.update())

    def onExit(self):
        getLogger().getChild(LOG_TAG).debug("Exit %s" % (type(self).__name__))

    def onDraw(self):
        for i in range(self.ctx.strip.numPixels()):
            c = 0
            if i == self.index:
                c = self.color
            self.ctx.strip.setPixelColor(i,c)
        self.ctx.strip.show()

    async def update(self):
        while True:
            await asyncio.sleep(0.1)
            self.index -=1
            self.index %= 4

