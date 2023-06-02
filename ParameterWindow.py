# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'parameter_window.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_ParameterWindow(object):
    def setupUi(self, ParameterWindow):
        if not ParameterWindow.objectName():
            ParameterWindow.setObjectName(u"ParameterWindow")
        ParameterWindow.resize(850, 789)
        self.centralwidget = QWidget(ParameterWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.imageDisplay = QLabel(self.centralwidget)
        self.imageDisplay.setObjectName(u"imageDisplay")
        self.imageDisplay.setGeometry(QRect(20, 20, 808, 608))
        self.imageDisplay.setScaledContents(True)
        self.buttonBox = QDialogButtonBox(self.centralwidget)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(630, 700, 192, 28))
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.updateImageButton = QPushButton(self.centralwidget)
        self.updateImageButton.setObjectName(u"updateImageButton")
        self.updateImageButton.setGeometry(QRect(630, 660, 192, 28))
        self.exposureSlider = QSlider(self.centralwidget)
        self.exposureSlider.setObjectName(u"exposureSlider")
        self.exposureSlider.setGeometry(QRect(100, 700, 481, 22))
        self.exposureSlider.setMinimum(0)
        self.exposureSlider.setMaximum(10)
        self.exposureSlider.setOrientation(Qt.Horizontal)
        self.exposureSlider.setTickPosition(QSlider.TicksBelow)
        self.exposureSlider.setTickInterval(1)
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 700, 91, 16))
        self.ROIButton = QPushButton(self.centralwidget)
        self.ROIButton.setObjectName(u"ROIButton")
        self.ROIButton.setGeometry(QRect(10, 660, 151, 28))
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(170, 665, 301, 16))
        ParameterWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(ParameterWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 850, 26))
        ParameterWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(ParameterWindow)
        self.statusbar.setObjectName(u"statusbar")
        ParameterWindow.setStatusBar(self.statusbar)

        self.retranslateUi(ParameterWindow)

        QMetaObject.connectSlotsByName(ParameterWindow)
    # setupUi

    def retranslateUi(self, ParameterWindow):
        ParameterWindow.setWindowTitle(QCoreApplication.translate("ParameterWindow", u"MainWindow", None))
        self.imageDisplay.setText("")
        self.updateImageButton.setText(QCoreApplication.translate("ParameterWindow", u"Update Image", None))
        self.label_2.setText(QCoreApplication.translate("ParameterWindow", u"Exposure (ms)", None))
        self.ROIButton.setText(QCoreApplication.translate("ParameterWindow", u"Select Region of Interest", None))
        self.label.setText(QCoreApplication.translate("ParameterWindow", u"(Press Enter or Space to confirm, press C to cancel)", None))
    # retranslateUi

