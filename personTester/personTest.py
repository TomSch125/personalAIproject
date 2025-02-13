# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'personTest.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QScrollArea, QVBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QIcon, QPixmap

import cv2
import sys
import os
import time
import numpy as np



pathDefectIms = "./images/defects/"
pathNormalIms = "./images/normal/"
names = []
normalNames = []
defectNames = []
curentNameIndex = -1

normalCorrect = 0
normalIncorrect = 0
defectCorrect = 0
defectIncorrect = 0

start = 0.0


class ScrollLabel(QScrollArea):
 
    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)
 
        self.setWidgetResizable(True)
 
        content = QWidget(self)
        self.setWidget(content)
 
        lay = QVBoxLayout(content)
 
        self.label = QLabel(content)

        self.label.setStyleSheet("QLabel{font-size: 18pt;}")
 
        lay.addWidget(self.label)



def initial():

    global names
    global defectNames
    global normalNames 


    defectNames = os.listdir(pathDefectIms)
    allNames = []

    for name in defectNames:
        #ims.append(cv2.imread(pathDefectIms+name))
        allNames.append(name)


    normalNames = os.listdir(pathNormalIms)

    for name in normalNames:
        # ims.append(cv2.imread(pathNormalIms+name))
        allNames.append(name)

    indexes_1 = np.random.randint(0, len(allNames)-1, size=int(len(allNames)/2))
    indexes_2 = np.random.randint(0, len(allNames)-1, size=int(len(allNames)/2))

    for i in range(0,len(indexes_1)):
        # tempIm = ims[indexes_1[i]]
        tempName = allNames[indexes_1[i]]

        allNames[indexes_1[i]] = allNames[indexes_2[i]]

        allNames[indexes_2[i]] = tempName

    names = allNames


def nextImage():
    global names
    global defectNames
    global normalNames 
    global curentNameIndex

    path = ""
    curentNameIndex = curentNameIndex + 1

    if checkEnd() == 0:

        name = names[curentNameIndex]

        if name in defectNames:
            path = pathDefectIms

        if name in normalNames:
            path = pathNormalIms

        pixmap = QPixmap()
        pixmap.load(path+name)
        ui.imageBox.label.setPixmap(pixmap)
    
def checkEnd():
    if curentNameIndex == len(names):
        now = time.perf_counter()
        end = now - start

        ui.DefectButton.hide()
        ui.normalButton.hide()

        pixmap = QPixmap()
        ui.imageBox.label.setPixmap(pixmap)
        ui.imageBox.label.setText("Correct Defects: " + str(defectCorrect)+"\n"+
        "Inorrect Defects: " + str(defectIncorrect)+"\n"+
        "Correct Normal: " + str(normalCorrect)+"\n"+
        "Incorrect Normal: " + str(normalIncorrect)+"\n"+
        "Accracy: " + str(100 * ((defectCorrect+normalCorrect)/(defectCorrect+normalCorrect+defectIncorrect+normalIncorrect)))+
        "\nTime: " + str(end)+" secconds")

        return 1
    return 0


@pyqtSlot()
def selectDefect(self):
    global defectCorrect
    global defectIncorrect


    if names[curentNameIndex] in defectNames:
        defectCorrect = defectCorrect + 1
    else:
        defectIncorrect = defectIncorrect + 1

    nextImage()


@pyqtSlot()
def selectNormal(self):
    global normalCorrect
    global normalIncorrect


    if names[curentNameIndex] in normalNames:
        normalCorrect = normalCorrect + 1
    else:
        normalIncorrect = normalIncorrect + 1

    nextImage()



@pyqtSlot()
def start(self):
    global start
    start = time.perf_counter()
    ui.startButton.hide()
    ui.DefectButton.show()
    ui.normalButton.show()

    initial()
    nextImage()


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1930, 1080)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")

        # self.imageBox = QtWidgets.QLabel(self.centralwidget)
        # self.imageBox.setText("")
        # self.imageBox.setObjectName("imageBox")
        # self.imageBox.setMaximumHeight(256)
        # self.imageBox.setStyleSheet("border :3px solid black;")

        # #self.imageBox.setScaledContents(True)
        # self.verticalLayout.addWidget(self.imageBox)

        self.imageBox = ScrollLabel(self.centralwidget)
        self.imageBox.setObjectName("imageBox")
        self.imageBox.label.setText("")
        self.imageBox.setMaximumHeight(400)
        self.imageBox.label.setMaximumHeight(256)
        self.verticalLayout.addWidget(self.imageBox)



        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        self.startButton.setMinimumSize(QtCore.QSize(0, 100))
        self.startButton.setObjectName("startButton")

        self.horizontalLayout.addWidget(self.startButton)
        self.DefectButton = QtWidgets.QPushButton(self.centralwidget)
        self.DefectButton.setMinimumSize(QtCore.QSize(100, 100))
        self.DefectButton.setBaseSize(QtCore.QSize(0, 0))
        self.DefectButton.setObjectName("DefectButton")
        self.DefectButton.hide()

        self.horizontalLayout.addWidget(self.DefectButton)
        self.normalButton = QtWidgets.QPushButton(self.centralwidget)
        self.normalButton.setMinimumSize(QtCore.QSize(100, 100))
        self.normalButton.setObjectName("normalButton")
        self.normalButton.hide()


        self.horizontalLayout.addWidget(self.normalButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.setStretch(0, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1049, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        # link buttons
        self.startButton.clicked.connect(start)
        self.DefectButton.clicked.connect(selectDefect)
        self.normalButton.clicked.connect(selectNormal)


        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.startButton.setText(_translate("MainWindow", "Start"))
        self.DefectButton.setText(_translate("MainWindow", "Defect"))
        self.normalButton.setText(_translate("MainWindow", "Normal"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.showMaximized()
    sys.exit(app.exec_())


