import asyncio
import janus
import serial.aio

from rainbowraceway import AdminController, RaceController,TrikeCtx
from rfid_reader import MockTagReader
from utils import async_cancel, CancelToken

if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    trikeCtx = TrikeCtx.createMockCtx()
    cancelToken = CancelToken(loop)

    tagStream = MockTagReader(cancelToken,4)
    taskController = AdminController(loop, cancelToken,trikeCtx)

    tasks = []
    tasks.append(taskController.createTask(loop, tagStream))
    tasks.append(loop.create_task(async_cancel(cancelToken, 20)))
    return_value = loop.run_until_complete(asyncio.gather(*tasks))