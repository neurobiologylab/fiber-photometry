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


class SettingsUI(object):
    def setupUi(self, Settings):
        if not Settings.objectName():
            Settings.setObjectName(u"Settings")
        Settings.resize(850, 789)
        self.wid_main = QWidget(Settings)
        self.wid_main.setObjectName(u"wid_main")
        self.lbl_display = QLabel(self.wid_main)
        self.lbl_display.setObjectName(u"lbl_display")
        self.lbl_display.setGeometry(QRect(20, 20, 808, 608))
        # self.lbl_display.setGeometry(QRect(20, 20, 1, 1))
        self.lbl_display.setScaledContents(True)
        self.dbb_ok_cancel = QDialogButtonBox(self.wid_main)
        self.dbb_ok_cancel.setObjectName(u"dbb_ok_cancel")
        self.dbb_ok_cancel.setGeometry(QRect(630, 700, 192, 28))
        self.dbb_ok_cancel.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.updateImageButton = QPushButton(self.wid_main)
        self.updateImageButton.setObjectName(u"updateImageButton")
        self.updateImageButton.setGeometry(QRect(630, 660, 192, 28))
        self.btn_roi = QPushButton(self.wid_main)
        self.btn_roi.setObjectName(u"btn_roi")
        self.btn_roi.setGeometry(QRect(10, 660, 151, 28))
        self.lbl_roi = QLabel(self.wid_main)
        self.lbl_roi.setObjectName(u"lbl_roi")
        self.lbl_roi.setGeometry(QRect(10, 640, 301, 16))

        self.lcd_test = QLabel(self.wid_main)
        self.lcd_test.setObjectName(u"lcd_test")
        # self.lcd_test.setProperty("intValue", "NA, NA, NA, NA")
        self.lcd_test.setGeometry(QRect(170, 660, 301, 25))





        self.wid_panel = QWidget(self.wid_main)
        self.wid_panel.setObjectName(u"wid_panel")
        self.wid_panel.setGeometry(QRect(10, 700, 486, 25))
        self.layout_horizontal = QHBoxLayout(self.wid_panel)
        self.layout_horizontal.setObjectName(u"layout_horizontal")
        self.layout_horizontal.setContentsMargins(0, 0, 0, 0)
        self.lbl_exposure = QLabel(self.wid_panel)
        self.lbl_exposure.setObjectName(u"lbl_exposure")

        self.layout_horizontal.addWidget(self.lbl_exposure)

        self.lcd_exposure = QLCDNumber(self.wid_panel)
        self.lcd_exposure.setObjectName(u"lcd_exposure")
        self.lcd_exposure.setProperty("intValue", 50)

        self.layout_horizontal.addWidget(self.lcd_exposure)

        self.lbl_freq_led = QLabel(self.wid_panel)
        self.lbl_freq_led.setObjectName(u"lbl_freq_led")

        self.layout_horizontal.addWidget(self.lbl_freq_led)
        


        self.lcd_freq_led = QLCDNumber(self.wid_panel)
        self.lcd_freq_led.setObjectName(u"lcd_freq_led")
        self.lcd_freq_led.setProperty("intValue", 5)

        self.layout_horizontal.addWidget(self.lcd_freq_led)

        self.lbl_freq_cam = QLabel(self.wid_panel)
        self.lbl_freq_cam.setObjectName(u"lbl_freq_cam")

        self.layout_horizontal.addWidget(self.lbl_freq_cam)

        self.lcd_freq_cam = QLCDNumber(self.wid_panel)
        self.lcd_freq_cam.setObjectName(u"lcd_freq_cam")
        self.lcd_freq_cam.setProperty("intValue", 10)

        self.layout_horizontal.addWidget(self.lcd_freq_cam)

        Settings.setCentralWidget(self.wid_main)
        self.menubar = QMenuBar(Settings)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 850, 21))
        Settings.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(Settings)
        self.statusbar.setObjectName(u"statusbar")
        Settings.setStatusBar(self.statusbar)

        self.retranslateUi(Settings)

        QMetaObject.connectSlotsByName(Settings)
    # setupUi

    def retranslateUi(self, Settings):
        Settings.setWindowTitle(QCoreApplication.translate("Settings", u"MainWindow", None))
        self.lbl_display.setText("")
        self.updateImageButton.setText(QCoreApplication.translate("Settings", u"Update Image", None))
        self.btn_roi.setText(QCoreApplication.translate("Settings", u"Select Region of Interest", None))
        self.lbl_roi.setText(QCoreApplication.translate("Settings", u"Press Enter or Space to confirm, press C to cancel.", None))
        self.lbl_exposure.setText(QCoreApplication.translate("Settings", u"Exposure (ms)", None))
        self.lbl_freq_led.setText(QCoreApplication.translate("Settings", u"LED Frequency (Hz)", None))
        self.lbl_freq_cam.setText(QCoreApplication.translate("Settings", u"Cam Frequency (Hz)", None))
    # retranslateUi

