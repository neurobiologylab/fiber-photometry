# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'parameter_window_temp.ui'
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
        self.ROIButton = QPushButton(self.centralwidget)
        self.ROIButton.setObjectName(u"ROIButton")
        self.ROIButton.setGeometry(QRect(10, 660, 151, 28))
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(170, 665, 301, 16))
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(10, 700, 486, 25))
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.widget)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout.addWidget(self.label_2)

        self.lcdNumber = QLCDNumber(self.widget)
        self.lcdNumber.setObjectName(u"lcdNumber")
        self.lcdNumber.setProperty("intValue", 50)

        self.horizontalLayout.addWidget(self.lcdNumber)

        self.label_3 = QLabel(self.widget)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout.addWidget(self.label_3)
        
        self.label_6 = QLabel(self.widget)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout.addWidget(self.label_6)

        self.lcdNumber_2 = QLCDNumber(self.widget)
        self.lcdNumber_2.setObjectName(u"lcdNumber_2")
        self.lcdNumber_2.setProperty("intValue", 5)

        self.horizontalLayout.addWidget(self.lcdNumber_2)

        self.label_4 = QLabel(self.widget)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout.addWidget(self.label_4)

        self.lcdNumber_3 = QLCDNumber(self.widget)
        self.lcdNumber_3.setObjectName(u"lcdNumber_3")
        self.lcdNumber_3.setProperty("intValue", 10)

        self.horizontalLayout.addWidget(self.lcdNumber_3)

        ParameterWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(ParameterWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 850, 21))
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
        self.ROIButton.setText(QCoreApplication.translate("ParameterWindow", u"Select Region of Interest", None))
        self.label.setText(QCoreApplication.translate("ParameterWindow", u"(Press Enter or Space to confirm, press C to cancel)", None))
        self.label_2.setText(QCoreApplication.translate("ParameterWindow", u"Exposure (ms)", None))
        self.label_3.setText(QCoreApplication.translate("ParameterWindow", u"LED Frequency (Hz)", None))
        self.label_4.setText(QCoreApplication.translate("ParameterWindow", u"Cam Frequency (Hz)", None))
    # retranslateUi

