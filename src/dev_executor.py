import asyncio
import janus
import serial
import serial.aio

from rainbowraceway import AdminController,TagStream, async_cancel
from utils import CancelToken
from rfid_reader import MockTagReader

from rfid_reader import MockTagReader
from trike_ctx import TrikeCtx


async def enqueueTags(src,q):
    async for tag in src:
        q.put(tag)

if __name__ == "__main__":
    trikeCtx = TrikeCtx.createProductionCtx()
    loop = asyncio.get_event_loop()
    cancelToken = CancelToken(loop)

    queue = janus.Queue(loop=loop)
    taskController = AdminController(loop, cancelToken, trikeCtx)
    tasks = []

    tasks.append(enqueueTags(MockTagReader(cancelToken,2),queue.sync_q))
    tasks.append(taskController.createTask(loop, TagStream(queue.async_q)))
    tasks.append(loop.create_task(async_cancel(cancelToken, 20)))
    loop.run_until_complete(asyncio.gather(*tasks))

