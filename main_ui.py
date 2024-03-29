from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2 import QtCore
from widget import MyMplCanvas

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


        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)

        # Create r1 with self.lbl_name
        self.r1_layout = QHBoxLayout()
        self.lbl_name = QLabel("<font color='red'>*</font> Experimental Animal\'s ID:")
        self.lbl_name.setFixedWidth(150) 
        self.txt_name = QLineEdit()
        self.txt_name.setFixedWidth(250) 
        self.txt_name.setObjectName(u"txt_name")
        self.btn_exp_init = QPushButton("New Experiment Initialization")
        self.btn_exp_init.setFixedWidth(180) 
        self.btn_exp_init.setObjectName(u"btn_exp_init")
        self.r1_layout.addWidget(self.lbl_name)
        self.r1_layout.addWidget(self.txt_name)
        self.r1_layout.addWidget(self.btn_exp_init)

        # Create r2 with self.txt_name, self.btn_roi, and self.btn_exp_init horizontally
        self.r2_layout = QHBoxLayout()
        self.lbl_roi = QLabel("<font color='red'>*</font> Select the region of interest: press 'Enter' or 'Space' to confirm, press C to cancel.")
        self.lbl_roi.setFixedWidth(405) 
        self.btn_roi = QPushButton("Select the Region of Interest")
        self.btn_roi.setFixedWidth(180) 
        self.btn_roi.setObjectName(u"btn_roi")
        self.r2_layout.addWidget(self.lbl_roi)
        self.r2_layout.addWidget(self.btn_roi)
        self.col1_layout.addLayout(self.r2_layout)
        self.col1_layout.addLayout(self.r1_layout)

        # Create r3 with self.btn_plot, self.chk_record, and self.btn_stop horizontally
        self.r3_layout = QHBoxLayout()
        self.chk_record = QCheckBox("Save Imgs")
        self.chk_record.setObjectName(u"chk_record")
        self.btn_plot = QPushButton("Plot")
        self.btn_plot.setFixedWidth(50) 
        self.btn_plot.setObjectName(u"btn_plot")
        self.lbl_freq = QLabel("Frequency:")
        self.lcd_freq = QLCDNumber()
        self.lcd_freq.setObjectName(u"lcd_freq")
        self.lcd_freq.setProperty("intValue", 0)
        self.lbl_time = QLabel("No.seconds:")
        self.lcd_time = QLCDNumber()
        self.lcd_time.setObjectName(u"lcd_time")
        self.lcd_time.setProperty("intValue", 0)
        self.btn_stop = QPushButton("Stop && Save Experiment Data")
        self.btn_stop.setFixedWidth(180) 
        self.btn_stop.setObjectName(u"btn_stop")
        self.r3_layout.addWidget(self.lbl_freq)
        self.r3_layout.addWidget(self.lcd_freq)
        self.r3_layout.addWidget(self.lbl_time)
        self.r3_layout.addWidget(self.lcd_time)
        self.r3_layout.addWidget(self.chk_record)
        self.r3_layout.addWidget(self.btn_plot)
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
        purple_color = "#8C6BB1"
        blue_color = "#2C82C9"
        red_color = "#E15759"
        black_color = "#000000"
        orange_color = "#FFA500"
        self.canvas_chn1 = MyMplCanvas(purple_color)
        self.canvas_chn1.setFixedHeight(200)
        self.canvas_chn1.setObjectName(u"canvas_chn1")
        self.canvas_chn2 = MyMplCanvas(blue_color)
        self.canvas_chn2.setFixedHeight(200)
        self.canvas_chn2.setObjectName(u"canvas_chn2")
        self.canvas_chn3 = MyMplCanvas(red_color)
        self.canvas_chn3.setFixedHeight(200)
        self.canvas_chn3.setObjectName(u"canvas_chn3")


        self.lbl_chn1 = QLabel("Channel 1")
        self.lbl_chn1.setFont(font)
        self.lbl_chn2 = QLabel("Channel 2")
        self.lbl_chn2.setFont(font)
        self.lbl_chn3 = QLabel("Channel 3")
        self.lbl_chn3.setFont(font)



        self.layout.addWidget(self.lbl_chn1, 1, 0, 1, 2)
        self.layout.addWidget(self.canvas_chn1, 2, 0, 1, 2)
        self.layout.addWidget(self.lbl_chn2, 3, 0, 1, 2)
        self.layout.addWidget(self.canvas_chn2, 4, 0, 1, 2)
        self.layout.addWidget(self.lbl_chn3, 5, 0, 1, 2)
        self.layout.addWidget(self.canvas_chn3, 6, 0, 1, 2)


        MainWindow.setCentralWidget(self.main_widget)
        QMetaObject.connectSlotsByName(MainWindow)