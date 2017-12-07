import os,sys

# The application when running will dynamically pull potential tag
# actions via introspection. In order find the files, sys.path is
# modified. As long as the compiled binary is somewhere in the
# repository the correct path will be found

def prependSearchPaths(folder):
    s = os.path.abspath(__file__)
    dir_chain = s.split('\\')[0:-1]
    for i in range(len(dir_chain),0,-1):
        path = "\\".join(dir_chain[:i]+["src"])
        if os.path.isdir(path):
            sys.path = [path] + sys.path

prependSearchPaths("src")

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QListWidgetItem,QErrorMessage
from tag_manager_gui import Ui_TagManager

import serial
import serial.tools.list_ports
import threading

import admin_behaviours,race_behaviours #these are not unused
import asyncio                          #TODO:move to hidden module hook for pyInstaller
import dynamic_types
import introspect
import tag_map_generation
import yr903

TAG_ROLE = 36
ASSOC_ROLE = 37
ASSOC_TYPE_ROLE = 38

try:
    import tags as tag_module
except:
    pass #Pass for now a MessageDialog will be launched once the context is established



class TagManager(Ui_TagManager):

    actionModules = ['admin_behaviours','race_behaviours']

    ############################
    ## Initializers
    ############################

    def __init__(self, window):
        Ui_TagManager.__init__(self)
        self.setupUi(window)

        self.serial_device = None
        self.isScanning = False
        self.init()
        self.wire()

    def init(self):
        self.verifyModuleLoads()
        self.initPorts()
        self.initActionList()

    def initActionList(self):
        for modulename in self.actionModules:
            for x in introspect.getAssociatedObjects(globals()[modulename]):
                item = QListWidgetItem("%s.%s (%s)" % (modulename, x.association, x.name))
                item.setData(ASSOC_ROLE, x.association)
                item.setData(ASSOC_TYPE_ROLE, modulename.split('_')[0])
                self.actionList.addItem(item)

    def initPorts(self):
        ports = self.getAvailablePorts()
        for p in ports:
            self.availablePorts.addItem(p.description, p.device)

    def wire(self):
        self.scanButton.clicked.connect(self.scanToggle)

        self.writeButton.clicked.connect(self.writeTagMapsToFile)
        self.actionList.selectionModel().currentChanged.connect(lambda a, b: self.writeButton.setEnabled(True))

    def verifyModuleLoads(self):
        errorDetected = False
        for modulename in self.actionModules+[tag_module.__name__]:
            if modulename not in sys.modules:
                self.log("Module could not be loaded(%s) Most likely caused by a syntax error" % (modulename))
                errorDetected = True

        if errorDetected:
           self.showError( "There was an error loading some Modules. Check Log for more information")

    ############################
    ## Signal Hooks
    ############################

    def writeTagMapsToFile(self):

        item = self.actionList.currentItem()
        association = dynamic_types.typeFromString(item.data(ASSOC_ROLE))
        target_map_name = item.data(ASSOC_TYPE_ROLE)+"_tags"

        for index in range(self.tagList.count()):
            item = self.tagList.item(index)
            tag = item.data(TAG_ROLE)

            #Remove from other TagMaps to avoid Conflicts
            for map_name in tag_map_generation.getMapNames():
                d = getattr(tag_module, map_name)
                if tag in d:
                    del d[tag]

            getattr(tag_module,target_map_name)[tag] = association #Set value in the appropriate map

        tag_map_generation.writeback(tag_module.__file__, tag_module.admin_tags,tag_module.race_tags)
        self.log("Tags Written to disk")

    def scanToggle(self):
        if self.scanButton.isChecked():
            ser = self.createSerialConnectionToSelectedPort()
            if ser == None:
                self.log("No Serial Device Found")
                self.scanButton.setChecked(False)
                return
            self.initiateTagScan(ser)
        else:
            self.log("Stopping Scan")
            self.scanner.cancel()

    ############################
    ## Helper Funcs
    ############################

    def log(self,msg):
        self.logBox.addItem(msg)
        self.logBox.scrollToBottom()

    def showError(msg):
        q = QErrorMessage()
        q.showMessage(msg)
        q.exec_()

    def getAvailablePorts(self):
        ports = list(serial.tools.list_ports.comports())
        return ports

    def createSerialConnectionToSelectedPort(self):
        i = self.availablePorts.currentIndex()
        device = self.availablePorts.itemData(i)
        if not device:
            return None
        try:
            ser = serial.Serial(port=device, bytesize=8, stopbits=1, timeout=0.05)
            ser.baudrate = 115200
        except:
            return None
        else:
            return ser

    def initiateTagScan(self,ser):
        threading.Thread(target=self.scanForTags,args=(ser,)).start()


    def scanForTags(self,serial):
        self.log("Scan Started")
        self.tagList.clear()

        tag_set = set([])
        def onTag(tag):
            if tag not in tag_set:
                self.addTagToList(tag)
                self.log(tag + " Detected")
            tag_set.add(tag)

        with yr903.Yr903(serial, onTag) as Y:
            self.scanner = Y
            Y.startRealtimeMode()

        self.scanner = None
        self.log("Scan Stopped")
        serial.close()
        self.scanButton.setChecked(False)

    def addTagToList(self,tag):
        s = ""
        for map_name in tag_map_generation.getMapNames():
            d = getattr(tag_module, map_name)
            if tag in d:
                s = "(%s)" % (d[tag])
                break

        item = QListWidgetItem(tag + s)
        item.setData(TAG_ROLE, tag)
        self.tagList.addItem(item)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()

    _ = TagManager(window)
    window.show()
    sys.exit(app.exec_())