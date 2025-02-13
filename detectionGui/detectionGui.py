# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'detectionGui.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!


import tile_methods as tm
import contour_find as cf

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QScrollArea, QVBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QIcon, QPixmap

import matplotlib.pyplot as plt
import numpy as np
import PIL
import tensorflow as tf

from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential


import cv2
import sys
import os
import time

names = []
cvImages = []
imageBatches = []
defects = []
imageI = 0
defectI = 1

tileSize = 64
overlap = 20

model = None
modelAug = None

path = "../allCropped/"
batchSize = 1
batchIndex = 0

def cv_to_qt(img):
    rgbIm = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w, channels = rgbIm.shape
    dataPerRow = channels * w
    qtImg = QtGui.QImage(rgbIm.data, w, h, dataPerRow, QtGui.QImage.Format_RGB888)
    return QPixmap.fromImage(qtImg)

def load_models():
    global model
    global modelAug

    model = keras.models.load_model("../inspection_model")
    modelAug = keras.models.load_model("../inspection_model_aug")

def importImages():
    global names 
    global imageBatches
    names = os.listdir(path)

    nameNum = 0
    batch = []
    for name in names:
        im = cv2.imread(path+name)
        cvImages.append(im)
        batch.append(im)
        nameNum = nameNum + 1
        if nameNum == batchSize:
            imageBatches.append(batch)
            nameNum = 0
            batch = []


def contourInspect():
    threshold = ui.cMinSpinBox.value()
    pixThresh = ui.pixMaxSpinBox.value()
    lighBlur = ui.lightBlurSpinBox.value()
    errosion = ui.erosionSpinBox.value()
    blur = ui.blurSpinBox.value()

    # for image in cvImages:

    for image in imageBatches[batchIndex]:
        imDefects = [image]
        #start = time.perf_counter()
        tiles = tm.tileImage(image,tileSize,tileSize,overlap)
        #end = time.perf_counter() - start

        for row in tiles:
            for tile in row:
                # start = time.perf_counter()
                result, imageMean, blobMean,blob_area, exitCode = cf.twoPassInspection(tile.roi,threshold, pixThresh, lighBlur, errosion, blur)
                # end = time.perf_counter() - start
                if exitCode == 0:
                    imDefects.append(result)
        if len(imDefects) >= 1:
            defects.append(imDefects)
        #print(".", len(imageBatches[batchIndex]))


def cnnInspect():
    curModel = None
    if ui.CNN_Model_Check.isChecked() == True:
        curModel = model
    if ui.CNN_Model_Aug_Check.isChecked() == True:
        curModel = modelAug


    for image in imageBatches[batchIndex]:
        imDefects = [image]
        tiles = tm.tileImage(image,tileSize,tileSize,overlap)

        #mainTensor = None
        imarray = []

        for row in tiles:
            for tile in row:
                # convert cv2 to tensor flow
                start = time.perf_counter()
                tileIm = tile.roi
                tileImRGB = cv2.cvtColor(tileIm, cv2.COLOR_BGR2RGB)

                imarray.append(tileImRGB)
 
        arg = tf.convert_to_tensor(imarray, dtype=tf.float32)
        # predictions = curModel.predict(mainTensor)
        predictions = curModel.predict(arg)
        indices = np.where(predictions < ui.confidenceSpin.value())

        for i in indices[0]:
            rowNum = int(i/len(tiles[0]))
            rowIndent = i%len(tiles[0])
            imDefects.append(tiles[rowNum][rowIndent].roi)

        if len(imDefects) >= 1:
            defects.append(imDefects)


def nextDefect():
    global defectI
    global imageI

    if (imageI < len(defects)) and (defectI  < len(defects[imageI])):

        if len(defects) > 0:
            image = defects[imageI][0]
            pixmap = cv_to_qt(image)
            ui.ImageBox.label.setPixmap(pixmap)

            tileIm = defects[imageI][defectI]
            pixmapTile = cv_to_qt(tileIm)
            ui.defectLable.setPixmap(pixmapTile)

            if len(defects[imageI])-1 == defectI:
                defectI = 1
                imageI = imageI + 1
            else:
                defectI = defectI + 1



@pyqtSlot()
def nextDefectSlot(self):
    nextDefect()


@pyqtSlot()
def start(self):
    global defects
    global batchIndex
    global imageI
    imageI = 0
    defects = []
    ui.defectLable.clear()
    ui.ImageBox.label.clear()



    if batchIndex >= len(imageBatches):
        return
    
    if ui.Contour_Check.isChecked() == True:
        start = time.perf_counter()
        contourInspect()
        end = time.perf_counter() - start
        nextDefect()

    if ui.CNN_Check.isChecked() == True:
        start = time.perf_counter()
        cnnInspect()
        end = time.perf_counter() - start
        nextDefect()

    ui.timeLabel.setText("{} Image Took: {:.2f}s".format(batchSize,end))

    batchIndex = batchIndex + 1

    

@pyqtSlot()
def selectCNN(self):
    if self.isChecked() == True:
        ui.Contour_Check.setChecked(False)

@pyqtSlot()
def selectContour(self):
    if self.isChecked() == True:
        ui.CNN_Check.setChecked(False)

@pyqtSlot()
def selectModelBin(self):
    if self.isChecked() == True:
        ui.CNN_Model_Aug_Check.setChecked(False)

@pyqtSlot()
def selectModelBin(self):
    if self.isChecked() == True:
        ui.CNN_Model_Aug_Check.setChecked(False)

@pyqtSlot()
def selectModelBinAug(self):
    if self.isChecked() == True:
        ui.CNN_Model_Check.setChecked(False)

@pyqtSlot()
def importButtonPress(self, mainwidow):
    global path
    folderpath = QtWidgets.QFileDialog.getExistingDirectory(None, "Select one or more files to open", "C:/")
    path = folderpath + "/"
    importImages()

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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1101, 677)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.LHS_Vertical = QtWidgets.QVBoxLayout()
        self.LHS_Vertical.setObjectName("LHS_Vertical")
        self.importButton = QtWidgets.QPushButton(self.centralwidget)
        self.importButton.setObjectName("importButton")
        self.importButton.clicked.connect(lambda:importButtonPress(self.Contour_Check, self))

        # self.importButton.hide()

        self.LHS_Vertical.addWidget(self.importButton)
        self.line_6 = QtWidgets.QFrame(self.centralwidget)
        self.line_6.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line_6.setLineWidth(5)
        self.line_6.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_6.setObjectName("line_6")
        self.LHS_Vertical.addWidget(self.line_6)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.defectLable = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.defectLable.sizePolicy().hasHeightForWidth())
        self.defectLable.setSizePolicy(sizePolicy)
        self.defectLable.setMinimumSize(QtCore.QSize(256, 256))
        self.defectLable.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.defectLable.setText("")
        self.defectLable.setScaledContents(True)
        self.defectLable.setObjectName("defectLable")
        self.horizontalLayout_7.addWidget(self.defectLable)
        self.LHS_Vertical.addLayout(self.horizontalLayout_7)
        self.line_7 = QtWidgets.QFrame(self.centralwidget)
        self.line_7.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line_7.setLineWidth(5)
        self.line_7.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_7.setObjectName("line_7")
        self.LHS_Vertical.addWidget(self.line_7)

        self.Next = QtWidgets.QPushButton(self.centralwidget)
        self.Next.setObjectName("Next")
        self.Next.clicked.connect(nextDefectSlot)


        self.LHS_Vertical.addWidget(self.Next)

        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        self.startButton.setObjectName("startButton")
        self.startButton.clicked.connect(start)


        self.LHS_Vertical.addWidget(self.startButton)

        self.timeLabel = QtWidgets.QLabel(self.centralwidget)
        self.timeLabel.setObjectName("timeLabel")
        self.timeLabel.setMaximumHeight(30)
        self.LHS_Vertical.addWidget(self.timeLabel)

        self.stopButton = QtWidgets.QPushButton(self.centralwidget)
        self.stopButton.setObjectName("stopButton")
        self.stopButton.hide()

        self.LHS_Vertical.addWidget(self.stopButton)
        self.horizontalLayout.addLayout(self.LHS_Vertical)
        self.line_5 = QtWidgets.QFrame(self.centralwidget)
        self.line_5.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line_5.setLineWidth(5)
        self.line_5.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_5.setObjectName("line_5")
        self.horizontalLayout.addWidget(self.line_5)
        self.RHS_Vertical = QtWidgets.QVBoxLayout()
        self.RHS_Vertical.setObjectName("RHS_Vertical")

        self.ImageBox = ScrollLabel(self.centralwidget)
        self.ImageBox.setObjectName("ImageBox")
        self.ImageBox.label.setText("")
        self.ImageBox.label.setMaximumHeight(256)

        self.RHS_Vertical.addWidget(self.ImageBox)

        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setMinimumSize(QtCore.QSize(0, 0))
        self.line.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.line.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line.setLineWidth(5)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setObjectName("line")
        self.RHS_Vertical.addWidget(self.line)
        self.LHS_BottomHalf = QtWidgets.QHBoxLayout()
        self.LHS_BottomHalf.setObjectName("LHS_BottomHalf")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.methodsLabel = QtWidgets.QLabel(self.centralwidget)
        self.methodsLabel.setMaximumSize(QtCore.QSize(16777215, 40))
        self.methodsLabel.setObjectName("methodsLabel")
        self.verticalLayout_2.addWidget(self.methodsLabel)
        self.CNN_Check = QtWidgets.QCheckBox(self.centralwidget)

        self.CNN_Check.setTristate(False)
        self.CNN_Check.setObjectName("CNN_Check")
        self.CNN_Check.setChecked(True)
        self.CNN_Check.stateChanged.connect(lambda:selectCNN(self.CNN_Check))
        

        self.verticalLayout_2.addWidget(self.CNN_Check)
        self.Contour_Check = QtWidgets.QCheckBox(self.centralwidget)
        self.Contour_Check.setObjectName("Contour_Check")
        self.Contour_Check.stateChanged.connect(lambda:selectContour(self.Contour_Check))


        self.verticalLayout_2.addWidget(self.Contour_Check)
        self.LHS_BottomHalf.addLayout(self.verticalLayout_2)
        self.line_3 = QtWidgets.QFrame(self.centralwidget)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line_3.setLineWidth(5)
        self.line_3.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_3.setObjectName("line_3")
        self.LHS_BottomHalf.addWidget(self.line_3)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.contourLable = QtWidgets.QLabel(self.centralwidget)
        self.contourLable.setMaximumSize(QtCore.QSize(16777215, 40))
        self.contourLable.setFrameShadow(QtWidgets.QFrame.Plain)
        self.contourLable.setObjectName("contourLable")
        self.verticalLayout.addWidget(self.contourLable)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.cMinLabel = QtWidgets.QLabel(self.centralwidget)
        self.cMinLabel.setObjectName("cMinLabel")
        self.horizontalLayout_2.addWidget(self.cMinLabel)
        self.cMinSpinBox = QtWidgets.QSpinBox(self.centralwidget)
        self.cMinSpinBox.setMinimum(1)
        self.cMinSpinBox.setMaximum(1000)
        self.cMinSpinBox.setProperty("value", 50)
        self.cMinSpinBox.setObjectName("cMinSpinBox")
        self.horizontalLayout_2.addWidget(self.cMinSpinBox)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.pMaxValLable = QtWidgets.QLabel(self.centralwidget)
        self.pMaxValLable.setObjectName("pMaxValLable")
        self.horizontalLayout_3.addWidget(self.pMaxValLable)
        self.pixMaxSpinBox = QtWidgets.QSpinBox(self.centralwidget)
        self.pixMaxSpinBox.setMinimum(1)
        self.pixMaxSpinBox.setMaximum(255)
        self.pixMaxSpinBox.setSingleStep(1)
        self.pixMaxSpinBox.setProperty("value", 90)
        self.pixMaxSpinBox.setObjectName("pixMaxSpinBox")
        self.horizontalLayout_3.addWidget(self.pixMaxSpinBox)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.lightBlurLabel = QtWidgets.QLabel(self.centralwidget)
        self.lightBlurLabel.setObjectName("lightBlurLabel")
        self.horizontalLayout_4.addWidget(self.lightBlurLabel)
        self.lightBlurSpinBox = QtWidgets.QSpinBox(self.centralwidget)
        self.lightBlurSpinBox.setMinimum(1)
        self.lightBlurSpinBox.setMaximum(30)
        self.lightBlurSpinBox.setProperty("value", 6)
        self.lightBlurSpinBox.setObjectName("lightBlurSpinBox")
        self.horizontalLayout_4.addWidget(self.lightBlurSpinBox)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.erosionLabel = QtWidgets.QLabel(self.centralwidget)
        self.erosionLabel.setObjectName("erosionLabel")
        self.horizontalLayout_5.addWidget(self.erosionLabel)
        self.erosionSpinBox = QtWidgets.QSpinBox(self.centralwidget)
        self.erosionSpinBox.setMinimum(1)
        self.erosionSpinBox.setMaximum(30)
        self.erosionSpinBox.setProperty("value", 9)
        self.erosionSpinBox.setObjectName("erosionSpinBox")
        self.horizontalLayout_5.addWidget(self.erosionSpinBox)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.BlurLabel = QtWidgets.QLabel(self.centralwidget)
        self.BlurLabel.setObjectName("BlurLabel")
        self.horizontalLayout_6.addWidget(self.BlurLabel)
        self.blurSpinBox = QtWidgets.QSpinBox(self.centralwidget)
        self.blurSpinBox.setMinimum(1)
        self.blurSpinBox.setMaximum(30)
        self.blurSpinBox.setProperty("value", 19)
        self.blurSpinBox.setObjectName("blurSpinBox")
        self.horizontalLayout_6.addWidget(self.blurSpinBox)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        self.LHS_BottomHalf.addLayout(self.verticalLayout)
        self.line_4 = QtWidgets.QFrame(self.centralwidget)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line_4.setLineWidth(5)
        self.line_4.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_4.setObjectName("line_4")
        self.LHS_BottomHalf.addWidget(self.line_4)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.modelLable = QtWidgets.QLabel(self.centralwidget)
        self.modelLable.setMaximumSize(QtCore.QSize(16777215, 40))
        self.modelLable.setFrameShadow(QtWidgets.QFrame.Plain)
        self.modelLable.setObjectName("modelLable")
        self.verticalLayout_4.addWidget(self.modelLable)

        self.CNN_Model_Check = QtWidgets.QCheckBox(self.centralwidget)
        self.CNN_Model_Check.setObjectName("CNN_Model_Check")
        self.CNN_Model_Check.setChecked(True)
        self.CNN_Model_Check.stateChanged.connect(lambda:selectModelBin(self.CNN_Model_Check))


        self.verticalLayout_4.addWidget(self.CNN_Model_Check)
        self.CNN_Model_Aug_Check = QtWidgets.QCheckBox(self.centralwidget)
        self.CNN_Model_Aug_Check.setObjectName("CNN_Model_Aug_Check")
        self.CNN_Model_Aug_Check.stateChanged.connect(lambda:selectModelBinAug(self.CNN_Model_Aug_Check))
        self.verticalLayout_4.addWidget(self.CNN_Model_Aug_Check)

        self.horizontalLayout_Con = QtWidgets.QHBoxLayout()

        self.conLabel = QtWidgets.QLabel(self.centralwidget)
        self.conLabel.setObjectName("conLabel")
        self.horizontalLayout_Con.addWidget(self.conLabel)

        self.confidenceSpin = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.confidenceSpin.setMinimum(0.01)
        self.confidenceSpin.setMaximum(0.5)
        self.confidenceSpin.setSingleStep(0.01)
        self.confidenceSpin.setProperty("value", 0.02)
        self.confidenceSpin.setObjectName("confidenceSpin")
        self.horizontalLayout_Con.addWidget(self.confidenceSpin)

        self.verticalLayout_4.addLayout(self.horizontalLayout_Con)

        self.LHS_BottomHalf.addLayout(self.verticalLayout_4)
        self.RHS_Vertical.addLayout(self.LHS_BottomHalf)
        self.RHS_Vertical.setStretch(0, 1)
        self.horizontalLayout.addLayout(self.RHS_Vertical)
        self.horizontalLayout.setStretch(2, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1101, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.importButton.setText(_translate("MainWindow", "Import Images"))
        self.Next.setText(_translate("MainWindow", "Next"))
        self.startButton.setText(_translate("MainWindow", "Start"))
        self.stopButton.setText(_translate("MainWindow", "Stop"))
        self.methodsLabel.setText(_translate("MainWindow", "Inspection Methods:"))
        self.CNN_Check.setText(_translate("MainWindow", "CNN Inspect"))
        self.Contour_Check.setText(_translate("MainWindow", "Contour Inspect"))
        self.contourLable.setText(_translate("MainWindow", "Contour Inspect Params:"))
        self.cMinLabel.setText(_translate("MainWindow", "Contour min size:"))
        self.pMaxValLable.setText(_translate("MainWindow", "Pixle Max Value:"))
        self.lightBlurLabel.setText(_translate("MainWindow", "Light Blur:"))
        self.erosionLabel.setText(_translate("MainWindow", "Erosion:"))
        self.BlurLabel.setText(_translate("MainWindow", "Blur:"))
        self.modelLable.setText(_translate("MainWindow", "Model:"))
        self.CNN_Model_Check.setText(_translate("MainWindow", "Binary CNN"))
        self.CNN_Model_Aug_Check.setText(_translate("MainWindow", "Binary CNN + Data Augmentation"))
        self.conLabel.setText(_translate("MainWindow", "Confidence Threshold:"))
        self.timeLabel.setText(_translate("MainWindow", ""))


if __name__ == "__main__":
    import sys
    print("Loading Images")
    importImages()
    print("Loading Deep Learning Models")
    load_models()
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

