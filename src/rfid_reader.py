import asyncio
import janus
import serial
import serial.aio
import struct
import time
from collections import deque

import yr903Pkt

import tags
import random
class MockTagReader:

    def __init__(self, cancelToken, delay):
        self.cancelToken = cancelToken
        self.delay = delay
        self.tagList = self.scrapeTags()

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.cancelToken.isCancelled():
            raise StopAsyncIteration
        await asyncio.sleep(self.delay)
        return random.choice(self.tagList)

    def scrapeTags(self):
        return [ x for x in tags.admin_tags.keys()] + [x for x in tags.race_tags.keys()]


class RfidReader(asyncio.Protocol):
    

    def __init__(self,queue):
        self.buf = b''
        self.readerAddr = 1
        self.channel = 1
    
        self.queue = queue
    def connection_made(self, transport):
        self.transport = transport
        print("Connected to Reader")
        transport.serial.rts = False
        self.start = time.time()
        self.requestRealTimeTags()

    def data_received(self, data):
        #print("BUF:",self.buf.hex(), "Data:", data.hex())
        self.buf += data
        self.buf = self.parsePkt(self.buf)

    
    def connection_lost(self, exc):
        print('port closed')
        asyncio.get_event_loop().stop()

    def requestRealTimeTags(self):
        self.transport.serial.write(yr903Pkt.createRealTimeInventoryPacket(self.readerAddr, self.channel))

    def parsePkt(self,buf):
        pktHeaderLen = 2

        if len(buf) < 4:
            return buf

        head,pktLen,addr,cmd = struct.unpack("BBBB",buf[:4])
        #print(head,pktLen,addr,cmd)
        if(head != yr903Pkt.header_id):
            print("ERRROROROR =====================");
            print (buf.hex())
            raise ValueError()
       
        if len(buf) < pktHeaderLen+pktLen:
            return buf

        if (pktLen == 0x0A and cmd == 0x89):
            self.requestRealTimeTags()
        else:
            self.pktHandler(buf)
        return buf[pktHeaderLen+pktLen:]

    def pktHandler(self,pkt):
        epc = pkt[10:-2]
        self.queue.put(epc.hex())


class TagStream:

    def __init__(self,queue):
        self.queue = queue
        self.enabled = True

    def cancel(self):
        self.enabled = False

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self.enabled:
            raise StopAsyncIteration()

        item = await self.queue.get()
        self.queue.task_done()
        return item

async def consume(q):
    tc = 0    
    async for tag in q:
        #priint("RECV: ",tag)
        tc +=1
    print ("Count:",tc)

async def cancel(wait,obj):
    await asyncio.sleep(wait)
    obj.cancel()


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    queue = janus.Queue(loop=loop);
    coro = serial.aio.create_serial_connection(loop, lambda: RfidReader(queue.sync_q), '/dev/ttyUSB0', baudrate=115200)
    ts = TagStream(queue.async_q)
    c = loop.create_task(consume(ts))
    c2 = loop.create_task(cancel(10,ts))
    #loop.create_task(cancel(2,coro.cancel()))
    loop.run_until_complete(asyncio.gather(coro,c,c2))
    loop.close()





