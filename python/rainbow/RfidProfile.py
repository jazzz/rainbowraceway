import time,sys

# import RFIDTest as RFID
import serial
import binascii
import select
from yr903 import Yr903

sleep_time = 0.02

class RfidProfiler:

    def __init__(self,runTime = 10):
        self.runTime = runTime
        self.invocationCount = 0

        self.buffer = bytearray()  # read buffer (4096)

        self.setupRfid()
        self.sumCards = 0


    def parseReaderMsg(self,buf):
        pass
        if len(buf) == 0:
            return
        self.buffer += buf  # append the new byte array to global parse buffer
        i = 0
        while (len(self.buffer) > 0):
            bt = self.buffer[i]

            if bt == 160:  # Msg init - \xA0
                tmpLen = self.buffer[i + 1] + 2
                tmpMsg = self.buffer[:tmpLen]
                tmpDir = self.buffer[i + 2]
                tmpData = tmpMsg[3:tmpLen - 1]

                if tmpLen == 12:  # last part of msg: total number of tags identified in the last round
                    totalCards = int(binascii.hexlify(tmpData[len(tmpData) - 4:]))
                    self.sumCards += totalCards
                else:
                    tmpCardID = binascii.hexlify(
                        tmpData[11:len(tmpData) - 1])  # Split the reader response and check card type
                    # print("CardID = " + tmpCardID)
                self.buffer = self.buffer[tmpLen:]
                i = -1
            i += 1


    def setupRfid(self):
        try:
            self.ser = serial.Serial(port="/dev/ttyUSB0", bytesize=8, stopbits=1, timeout=0.1)
            self.ser.baudrate = 115200
            mode = 1
            return True
        except:
            print
            "Cannot connect to reader. Make sure the pins are configured for USB and the reader is connected"
            return False

    def workLoop(self):

        self.ser.write(b'\xA0\x04\x01\x89\x01\xD1')  # ReadInstc
        # time.sleep(sleep_time)
        msg = self.ser.read(1024)

        self.parseReaderMsg(msg)


    def run(self):
        start = time.time()
        while (time.time()-start < self.runTime):
            self.workLoop()
            self.invocationCount += 1

        end = time.time()
        callsPerSec = self.invocationCount / float(end-start)
        print( "Trial Result: Runs %d  CallsPerSec: %f  Cards:%d CardsPerSec:%f"% (self.invocationCount, callsPerSec,self.sumCards, self.sumCards/float(end-start)))



import cProfile
if __name__ == "__main__":
    rp = RfidProfiler(2)
    # rp.run();



    cProfile.run('rp.run()')
