# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from pyqtgraph import PlotWidget


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(700, 525)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.layoutWidget = QWidget(self.centralwidget)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(11, 10, 681, 461))
        self.gridLayout_4 = QGridLayout(self.layoutWidget)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.horizontalSpacer = QSpacerItem(88, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer, 0, 0, 1, 1)

        self.label_3 = QLabel(self.layoutWidget)
        self.label_3.setObjectName(u"label_3")
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)

        self.gridLayout_3.addWidget(self.label_3, 0, 1, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(98, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer_2, 0, 2, 1, 1)

        self.PlotView = PlotWidget(self.layoutWidget)
        self.PlotView.setObjectName(u"PlotView")

        self.gridLayout_3.addWidget(self.PlotView, 1, 0, 1, 3)


        self.gridLayout_4.addLayout(self.gridLayout_3, 0, 1, 1, 1)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer_4 = QSpacerItem(28, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_4)

        self.label = QLabel(self.layoutWidget)
        self.label.setObjectName(u"label")
        self.label.setFont(font)

        self.horizontalLayout.addWidget(self.label)

        self.horizontalSpacer_3 = QSpacerItem(108, 17, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_3)

        self.label_2 = QLabel(self.layoutWidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font)

        self.horizontalLayout.addWidget(self.label_2)

        self.horizontalSpacer_5 = QSpacerItem(28, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_5)


        self.label_6 = QLabel(self.layoutWidget)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setFont(font)

        self.horizontalLayout.addWidget(self.label_6)

        self.horizontalSpacer_6 = QSpacerItem(28, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_6)

        self.horizontalLayout.setStretch(0, 2)
        self.horizontalLayout.setStretch(1, 2)
        self.horizontalLayout.setStretch(2, 3)
        self.horizontalLayout.setStretch(3, 2)
        self.horizontalLayout.setStretch(4, 2)
        self.horizontalLayout.setStretch(5, 2)

        self.gridLayout_2.addLayout(self.horizontalLayout, 0, 0, 1, 3)

        self.PlotView_2 = PlotWidget(self.layoutWidget)
        self.PlotView_2.setObjectName(u"PlotView_2")

        self.gridLayout_2.addWidget(self.PlotView_2, 1, 0, 1, 1)

        self.PlotView_3 = PlotWidget(self.layoutWidget)
        self.PlotView_3.setObjectName(u"PlotView_3")

        self.gridLayout_2.addWidget(self.PlotView_3, 1, 1, 1, 1)

        #I added this

        self.PlotView_4 = PlotWidget(self.layoutWidget)
        self.PlotView_4.setObjectName(u"PlotView_4")

        self.gridLayout_2.addWidget(self.PlotView_4, 1,2,1,1)


        self.gridLayout_4.addLayout(self.gridLayout_2, 1, 0, 1, 2)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.NewButton = QPushButton(self.layoutWidget)
        self.NewButton.setObjectName(u"NewButton")
        font1 = QFont()
        font1.setPointSize(14)
        font1.setBold(True)
        font1.setWeight(75)
        self.NewButton.setFont(font1)

        self.gridLayout.addWidget(self.NewButton, 0, 0, 1, 1)

        self.SetParametersButton = QPushButton(self.layoutWidget)
        self.SetParametersButton.setObjectName(u"SetParametersButton")
        self.SetParametersButton.setFont(font1)

        self.gridLayout.addWidget(self.SetParametersButton, 1, 0, 1, 1)

        self.PlotButton = QPushButton(self.layoutWidget)
        self.PlotButton.setObjectName(u"PlotButton")
        self.PlotButton.setFont(font1)

        self.gridLayout.addWidget(self.PlotButton, 2, 0, 1, 1)

        self.RecordButton = QPushButton(self.layoutWidget)
        self.RecordButton.setObjectName(u"RecordButton")
        self.RecordButton.setFont(font1)

        self.gridLayout.addWidget(self.RecordButton, 3, 0, 1, 1)

        self.StopButton = QPushButton(self.layoutWidget)
        self.StopButton.setObjectName(u"StopButton")
        self.StopButton.setFont(font1)

        self.gridLayout.addWidget(self.StopButton, 4, 0, 1, 1)


        self.gridLayout_4.addLayout(self.gridLayout, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 700, 26))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"dF/F Signal", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"470nm", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"405nm", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"590nm", None))
        self.NewButton.setText(QCoreApplication.translate("MainWindow", u"New", None))
        self.SetParametersButton.setText(QCoreApplication.translate("MainWindow", u"Set Parameters", None))
        self.PlotButton.setText(QCoreApplication.translate("MainWindow", u"Plot", None))
        self.RecordButton.setText(QCoreApplication.translate("MainWindow", u"Record", None))
        self.StopButton.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
    # retranslateUi

