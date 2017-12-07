import threading

import serial

import yr903Pkt


# This class handles Communication with a YR902 UHF RFID scanner
# Inputs:
#   -   Opened Serial(pySerial) object which is conssumed
#   -   Function to be executed when a new tag is received

class Yr903:
    enabled = False

    def __init__(self,serialObj,dataHandler):
        self.serial = serialObj
        self.dataHandler = dataHandler
        self.readerAddr = 1
        self.channel = 1

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.serial.close()

    def cancel(self):
        self.enabled = False

    def requestRealTimeTags(self):
        self.serial.write(yr903Pkt.createRealTimeInventoryPacket(self.readerAddr, self.channel))

    def processRealtimePkt(self,pktLen,pkt):
        if (pktLen == 0x0A and pkt[1] == 0x89):
            self.requestRealTimeTags()
        else:
            epc = pkt[8:-2]
            self.dataHandler(epc.hex())




    def startRealtimeMode(self):
        self.enabled = True
        self.requestRealTimeTags()
        while(self.enabled):
            msg = self.serial.read(2)
            if (len(msg)>1 and msg[0] == 0xA0):
                pktLen = msg[1]
                pkt = self.serial.read(pktLen)
                self.processRealtimePkt(pktLen,pkt)

if __name__ == "__main__":


    device = "COM14"	
    device = "/dev/ttyUSB0"
    print (device)
    serial = serial.Serial(port=device, bytesize=8, stopbits=1, timeout=0.05)
    serial.baudrate = 115200

    tagCount = 0
    def printData(byteData):
        print(byteData)

    with Yr903(serial,printData) as Y:
        threading.Timer(2,Y.cancel).start()
        Y.startRealtimeMode()

    # print("Total Tags Scanned: ",tagCount)

