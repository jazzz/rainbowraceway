# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'tag_manager.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_TagManager(object):
    def setupUi(self, TagManager):
        TagManager.setObjectName("TagManager")
        TagManager.resize(1042, 1164)
        self.centralwidget = QtWidgets.QWidget(TagManager)
        self.centralwidget.setObjectName("centralwidget")
        self.tagList = QtWidgets.QListWidget(self.centralwidget)
        self.tagList.setGeometry(QtCore.QRect(15, 41, 521, 711))
        self.tagList.setObjectName("tagList")
        self.scanButton = QtWidgets.QPushButton(self.centralwidget)
        self.scanButton.setGeometry(QtCore.QRect(550, 780, 131, 81))
        self.scanButton.setCheckable(True)
        self.scanButton.setObjectName("scanButton")
        self.actionList = QtWidgets.QListWidget(self.centralwidget)
        self.actionList.setGeometry(QtCore.QRect(550, 40, 481, 711))
        self.actionList.setObjectName("actionList")
        self.writeButton = QtWidgets.QPushButton(self.centralwidget)
        self.writeButton.setEnabled(False)
        self.writeButton.setGeometry(QtCore.QRect(700, 780, 121, 81))
        self.writeButton.setObjectName("writeButton")
        self.tagLabel = QtWidgets.QLabel(self.centralwidget)
        self.tagLabel.setGeometry(QtCore.QRect(17, 10, 261, 20))
        self.tagLabel.setObjectName("tagLabel")
        self.actionLabel = QtWidgets.QLabel(self.centralwidget)
        self.actionLabel.setGeometry(QtCore.QRect(550, 10, 261, 20))
        self.actionLabel.setObjectName("actionLabel")
        self.logBox = QtWidgets.QListWidget(self.centralwidget)
        self.logBox.setGeometry(QtCore.QRect(0, 890, 1031, 211))
        self.logBox.setObjectName("logBox")
        self.availablePorts = QtWidgets.QComboBox(self.centralwidget)
        self.availablePorts.setGeometry(QtCore.QRect(70, 780, 411, 41))
        self.availablePorts.setObjectName("availablePorts")
        TagManager.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(TagManager)
        self.statusbar.setObjectName("statusbar")
        TagManager.setStatusBar(self.statusbar)

        self.retranslateUi(TagManager)
        QtCore.QMetaObject.connectSlotsByName(TagManager)

    def retranslateUi(self, TagManager):
        _translate = QtCore.QCoreApplication.translate
        TagManager.setWindowTitle(_translate("TagManager", "Rainbow Raceway Tag Manager"))
        self.scanButton.setText(_translate("TagManager", "Scan"))
        self.writeButton.setText(_translate("TagManager", "Write"))
        self.tagLabel.setText(_translate("TagManager", "Scaned Tags"))
        self.actionLabel.setText(_translate("TagManager", "Available Behaviors"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    TagManager = QtWidgets.QMainWindow()
    ui = Ui_TagManager()
    ui.setupUi(TagManager)
    TagManager.show()
    sys.exit(app.exec_())

