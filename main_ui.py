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
from PySide2 import QtCore

from pyqtgraph import PlotWidget


class MainUI(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(700, 525)
        self.main_widget = QWidget(MainWindow)
        self.layout = QGridLayout(self.main_widget)

        # Create the first row with two columns
        self.col1_layout = QVBoxLayout()
        self.col2_layout = QVBoxLayout()

        # Create r1 with self.lbl_name
        self.r1_layout = QHBoxLayout()
        self.lbl_name = QLabel("<font color='red'>*</font> Experimenter\'s Name:")
        self.lbl_name.setFixedWidth(120) 
        self.txt_name = QLineEdit()
        self.txt_name.setFixedWidth(280) 
        self.txt_name.setObjectName(u"txt_name")
        self.btn_exp_init = QPushButton("New Experiment Initialization")
        self.btn_exp_init.setFixedWidth(200) 
        self.btn_exp_init.setObjectName(u"btn_exp_init")
        self.r1_layout.addWidget(self.lbl_name)
        self.r1_layout.addWidget(self.txt_name)
        self.r1_layout.addWidget(self.btn_exp_init)
        self.col1_layout.addLayout(self.r1_layout)

        # Create r2 with self.txt_name, self.btn_roi, and self.btn_exp_init horizontally
        self.r2_layout = QHBoxLayout()
        self.lbl_roi = QLabel("<font color='red'>*</font> Select the region of interest: press 'Enter' or 'Space' to confirm, press C to cancel.")
        self.lbl_roi.setFixedWidth(405) 
        self.btn_roi = QPushButton("Select the Region of Interest")
        self.btn_roi.setFixedWidth(200) 
        self.btn_roi.setObjectName(u"btn_roi")
        self.r2_layout.addWidget(self.lbl_roi)
        self.r2_layout.addWidget(self.btn_roi)
        self.col1_layout.addLayout(self.r2_layout)

        # Create r3 with self.btn_plot, self.btn_record, and self.btn_stop horizontally
        self.r3_layout = QHBoxLayout()
        self.btn_plot = QPushButton("Plot")
        self.btn_plot.setFixedWidth(200) 
        self.btn_plot.setObjectName(u"btn_plot")
        self.btn_record = QPushButton("Record")
        self.btn_record.setFixedWidth(200) 
        self.btn_record.setObjectName(u"btn_record")
        self.btn_stop = QPushButton("Stop && Save Experiment Data")
        self.btn_stop.setFixedWidth(200) 
        self.btn_stop.setObjectName(u"btn_stop")
        self.r3_layout.addWidget(self.btn_plot)
        self.r3_layout.addWidget(self.btn_record)
        self.r3_layout.addWidget(self.btn_stop)
        self.col1_layout.addLayout(self.r3_layout)

        # Add col1 to the layout
        self.layout.addLayout(self.col1_layout, 0, 0)

        # Create self.img_display and add it to col2
        self.img_display = QLabel()
        self.img_display.setObjectName(u"img_display")
        self.img_display.setFixedWidth(100)  # Set fixed width
        self.img_display.setFixedHeight(100)  # Set fixed height
        self.img_display.setAlignment(QtCore.Qt.AlignCenter)  # Align center
        self.col2_layout.addWidget(self.img_display)

        # Add col2 to the layout
        self.layout.addLayout(self.col2_layout, 0, 1)

        # Create plot widgets and place them in subsequent rows
        self.plot_chn1 = PlotWidget()
        self.plot_chn1.setObjectName(u"plot_chn1")
        self.plot_chn2 = PlotWidget()
        self.plot_chn2.setObjectName(u"plot_chn2")
        self.plot_chn3 = PlotWidget()
        self.plot_chn3.setObjectName(u"plot_chn3")
        self.plot_final = PlotWidget()
        self.plot_final.setObjectName(u"plot_final")

        self.layout.addWidget(self.plot_final, 1, 0, 1, 2)
        self.layout.addWidget(self.plot_chn1, 2, 0, 1, 2)
        self.layout.addWidget(self.plot_chn2, 3, 0, 1, 2)
        self.layout.addWidget(self.plot_chn3, 4, 0, 1, 2)

        MainWindow.setCentralWidget(self.main_widget)
        # self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)
        # self.retranslateUi(MainWindow)


    def setup_settings_tab(self):
        self.tab_settings_layout = QVBoxLayout(self.tab_settings)
        self.tab_settings_layout.setAlignment(QtCore.Qt.AlignTop)  # Align widgets to the top

        # Create the first row with lbl_name, txt_name, btn_roi, and btn_exp_init
        self.topline_layout = QHBoxLayout()
        self.lbl_name = QLabel("Experimenter's Name:")
        self.txt_name = QLineEdit()
        self.txt_name.setObjectName(u"txt_name")
        self.btn_roi = QPushButton("Region of Interest")
        self.btn_roi.setObjectName(u"btn_roi")
        self.btn_exp_init = QPushButton("Save")
        self.btn_exp_init.setObjectName(u"btn_exp_init")

        self.topline_layout.addWidget(self.lbl_name)
        self.topline_layout.addWidget(self.txt_name)
        self.topline_layout.addWidget(self.btn_roi)
        self.topline_layout.addWidget(self.btn_exp_init)

        self.tab_settings_layout.addLayout(self.topline_layout)

        self.img_display = QLabel()
        self.img_display.setFixedHeight(600)  # Set fixed height
        self.img_display.setAlignment(QtCore.Qt.AlignCenter)  # Align center
        self.tab_settings_layout.addWidget(self.img_display)

        self.tab_settings.setLayout(self.tab_settings_layout)

        # self.btn_roi.clicked.connect(self.select_roi)
        # self.btn_exp_init.clicked.connect(self.init_experiment_data)



    def setup_experiment_tab(self):
        self.tab_experiment_layout = QVBoxLayout(self.tab_experiment)

        # Create buttons and place them in a line at the top
        self.btn_plot = QPushButton("Plot")
        self.btn_plot.setObjectName(u"btn_plot")
        self.btn_record = QPushButton("Record")
        self.btn_record.setObjectName(u"btn_record")
        self.btn_stop = QPushButton("Stop")
        self.btn_stop.setObjectName(u"btn_stop")

        self.top_button_layout = QHBoxLayout()
        self.top_button_layout.addWidget(self.btn_plot)
        self.top_button_layout.addWidget(self.btn_record)
        self.top_button_layout.addWidget(self.btn_stop)
        # Link buttons to calling specific functions
        # self.btn_plot.clicked.connect(self.plotting)
        # self.btn_record.clicked.connect(self.recording)
        # self.btn_stop.clicked.connect(self.stop)

        self.tab_experiment_layout.addLayout(self.top_button_layout)

        # Create plot widgets
        self.plot_chn1 = PlotWidget()
        self.plot_chn1.setObjectName(u"plot_chn1")
        self.plot_chn2 = PlotWidget()
        self.plot_chn2.setObjectName(u"plot_chn2")
        self.plot_chn3 = PlotWidget()
        self.plot_chn3.setObjectName(u"plot_chn3")
        self.plot_final = PlotWidget()
        self.plot_final.setObjectName(u"plot_final")

        self.top_layout = QHBoxLayout()
        self.top_layout.addWidget(self.plot_final)

        self.bottom_layout = QHBoxLayout()
        self.bottom_layout.addWidget(self.plot_chn1)
        self.bottom_layout.addWidget(self.plot_chn2)
        self.bottom_layout.addWidget(self.plot_chn3)

        self.tab_experiment_layout.addLayout(self.top_layout)
        self.tab_experiment_layout.addLayout(self.bottom_layout)

        self.tab_experiment.setLayout(self.tab_experiment_layout)




        # self.wid_main = QWidget(MainWindow)
        # self.wid_main.setObjectName(u"wid_main")
        # self.layoutWidget = QWidget(self.wid_main)
        # self.layoutWidget.setObjectName(u"layoutWidget")
        # self.layoutWidget.setGeometry(QRect(11, 10, 681, 461))
        # self.gridLayout_4 = QGridLayout(self.layoutWidget)
        # self.gridLayout_4.setObjectName(u"gridLayout_4")
        # self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        # self.gridLayout_3 = QGridLayout()
        # self.gridLayout_3.setObjectName(u"gridLayout_3")
        # self.horizontalSpacer = QSpacerItem(88, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        # self.gridLayout_3.addItem(self.horizontalSpacer, 0, 0, 1, 1)

        # self.lbl_dff = QLabel(self.layoutWidget)
        # self.lbl_dff.setObjectName(u"lbl_dff")
        # font = QFont()
        # font.setPointSize(10)
        # font.setBold(True)
        # font.setWeight(75)
        # self.lbl_dff.setFont(font)

        # self.gridLayout_3.addWidget(self.lbl_dff, 0, 1, 1, 1)

        # self.horizontalSpacer_2 = QSpacerItem(98, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        # self.gridLayout_3.addItem(self.horizontalSpacer_2, 0, 2, 1, 1)

        # self.PlotView = PlotWidget(self.layoutWidget)
        # self.PlotView.setObjectName(u"PlotView")

        # self.gridLayout_3.addWidget(self.PlotView, 1, 0, 1, 3)


        # self.gridLayout_4.addLayout(self.gridLayout_3, 0, 1, 1, 1)

        # self.gridLayout_2 = QGridLayout()
        # self.gridLayout_2.setObjectName(u"gridLayout_2")
        # self.horizontalLayout = QHBoxLayout()
        # self.horizontalLayout.setObjectName(u"horizontalLayout")
        # self.horizontalSpacer_4 = QSpacerItem(28, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        # self.horizontalLayout.addItem(self.horizontalSpacer_4)

        # self.lbl_channel1 = QLabel(self.layoutWidget)
        # self.lbl_channel1.setObjectName(u"lbl_channel1")
        # self.lbl_channel1.setFont(font)

        # self.horizontalLayout.addWidget(self.lbl_channel1)

        # self.horizontalSpacer_3 = QSpacerItem(108, 17, QSizePolicy.Expanding, QSizePolicy.Minimum)

        # self.horizontalLayout.addItem(self.horizontalSpacer_3)

        # self.lbl_channel2 = QLabel(self.layoutWidget)
        # self.lbl_channel2.setObjectName(u"lbl_channel2")
        # self.lbl_channel2.setFont(font)

        # self.horizontalLayout.addWidget(self.lbl_channel2)

        # self.horizontalSpacer_5 = QSpacerItem(28, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        # self.horizontalLayout.addItem(self.horizontalSpacer_5)


        # self.lbl_channel3 = QLabel(self.layoutWidget)
        # self.lbl_channel3.setObjectName(u"lbl_channel3")
        # self.lbl_channel3.setFont(font)

        # self.horizontalLayout.addWidget(self.lbl_channel3)

        # self.horizontalSpacer_6 = QSpacerItem(28, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        # self.horizontalLayout.addItem(self.horizontalSpacer_6)

        # self.horizontalLayout.setStretch(0, 2)
        # self.horizontalLayout.setStretch(1, 2)
        # self.horizontalLayout.setStretch(2, 3)
        # self.horizontalLayout.setStretch(3, 2)
        # self.horizontalLayout.setStretch(4, 2)
        # self.horizontalLayout.setStretch(5, 2)

        # self.gridLayout_2.addLayout(self.horizontalLayout, 0, 0, 1, 3)

        # self.PlotView_2 = PlotWidget(self.layoutWidget)
        # self.PlotView_2.setObjectName(u"PlotView_2")

        # self.gridLayout_2.addWidget(self.PlotView_2, 1, 0, 1, 1)

        # self.PlotView_3 = PlotWidget(self.layoutWidget)
        # self.PlotView_3.setObjectName(u"PlotView_3")

        # self.gridLayout_2.addWidget(self.PlotView_3, 1, 1, 1, 1)

        # #I added this

        # self.PlotView_4 = PlotWidget(self.layoutWidget)
        # self.PlotView_4.setObjectName(u"PlotView_4")

        # self.gridLayout_2.addWidget(self.PlotView_4, 1,2,1,1)


        # self.gridLayout_4.addLayout(self.gridLayout_2, 1, 0, 1, 2)

        # self.gridLayout = QGridLayout()
        # self.gridLayout.setObjectName(u"gridLayout")
        # # self.NewButton = QPushButton(self.layoutWidget)
        # # self.NewButton.setObjectName(u"NewButton")
        # self.lbl_name = QLabel("Experimenter")
        # self.lbl_name.setObjectName(u"lbl_name")
        # self.gridLayout.addWidget(self.lbl_name, 0, 0, 1, 1)
        # self.txt_name = QLineEdit(self.layoutWidget)
        # self.txt_name.resize(QSize(50, 30))
        # self.txt_name.setObjectName(u"txt_name")
        # self.gridLayout.addWidget(self.txt_name, 1, 0, 1, 1)
        # font1 = QFont()
        # font1.setPointSize(11)
        # # font1.setBold(True)
        # # font1.setWeight(75)
        # # self.NewButton.setFont(font1)

        # # self.gridLayout.addWidget(self.NewButton, 0, 0, 1, 1)

        # self.SetParametersButton = QPushButton(self.layoutWidget)
        # self.SetParametersButton.setObjectName(u"SetParametersButton")
        # # self.SetParametersButton.setFont(font1)

        # self.gridLayout.addWidget(self.SetParametersButton, 2, 0, 1, 1)

        # self.btn_plot = QPushButton(self.layoutWidget)
        # self.btn_plot.setObjectName(u"btn_plot")
        # # self.btn_plot.setFont(font1)

        # self.gridLayout.addWidget(self.btn_plot, 3, 0, 1, 1)

        # self.btn_record = QPushButton(self.layoutWidget)
        # self.btn_record.setObjectName(u"btn_record")
        # # self.btn_record.setFont(font1)

        # self.gridLayout.addWidget(self.btn_record, 4, 0, 1, 1)

        # self.btn_stop = QPushButton(self.layoutWidget)
        # self.btn_stop.setObjectName(u"btn_stop")
        # # self.btn_stop.setFont(font1)

        # self.gridLayout.addWidget(self.btn_stop, 5, 0, 1, 1)


        # self.gridLayout_4.addLayout(self.gridLayout, 0, 0, 1, 1)

        # MainWindow.setCentralWidget(self.wid_main)
        # self.menubar = QMenuBar(MainWindow)
        # self.menubar.setObjectName(u"menubar")
        # self.menubar.setGeometry(QRect(0, 0, 700, 26))
        # MainWindow.setMenuBar(self.menubar)
        # self.statusbar = QStatusBar(MainWindow)
        # self.statusbar.setObjectName(u"statusbar")
        # MainWindow.setStatusBar(self.statusbar)

        # self.retranslateUi(MainWindow)

        # QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        # self.lbl_dff.setText(QCoreApplication.translate("MainWindow", u"dF/F Signal", None))
        # self.lbl_channel1.setText(QCoreApplication.translate("MainWindow", u"channel1", None))
        # self.lbl_channel2.setText(QCoreApplication.translate("MainWindow", u"channel2", None))
        # self.lbl_channel3.setText(QCoreApplication.translate("MainWindow", u"channel3", None))
        # self.NewButton.setText(QCoreApplication.translate("MainWindow", u"New", None))
        # self.SetParametersButton.setText(QCoreApplication.translate("MainWindow", u"Set Parameters", None))
        self.btn_plot.setText(QCoreApplication.translate("MainWindow", u"Plot", None))
        self.btn_record.setText(QCoreApplication.translate("MainWindow", u"Record", None))
        self.btn_stop.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
    # retranslateUi

