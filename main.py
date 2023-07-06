import os
import sys
import csv
import datetime
import time
import cv2
import copy
import numpy as np
import PySpin
import pyqtgraph as pg
import qimage2ndarray
from pathlib import Path
from collections import deque
from scipy.stats import zscore
from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QTabWidget, QMessageBox, QLineEdit
from PySide2.QtGui import QIcon, QPixmap, QImage
from PySide2 import QtCore
from flir import RecordingWorker, FLIRAcquisitionWorker, ROI

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("NBI Photometry")
        self.setWindowIcon(QIcon('nbi-logo.jpg'))

        self.main_widget = QWidget()
        self.layout = QVBoxLayout(self.main_widget)

        self.tab_widget = QTabWidget()

        self.tab_settings = QWidget()
        self.tab_experiment = QWidget()

        self.tab_widget.addTab(self.tab_settings, "Settings")
        self.tab_widget.addTab(self.tab_experiment, "Experiment")

        self.setup_settings_tab()
        self.setup_experiment_tab()

        self.layout.addWidget(self.tab_widget)
        self.setCentralWidget(self.main_widget)
        self.is_experiment_initialized = False
        self.show()

    def setup_settings_tab(self):
        self.tab_settings_layout = QVBoxLayout(self.tab_settings)
        self.tab_settings_layout.setAlignment(QtCore.Qt.AlignTop)  # Align widgets to the top

        # Create the first row with lbl_name, txt_name, btn_roi, and btn_save
        self.topline_layout = QHBoxLayout()
        self.lbl_name = QLabel("Experimenter's Name:")
        self.txt_name = QLineEdit()
        self.btn_roi = QPushButton("Region of Interest")
        self.btn_save = QPushButton("Save")

        self.topline_layout.addWidget(self.lbl_name)
        self.topline_layout.addWidget(self.txt_name)
        self.topline_layout.addWidget(self.btn_roi)
        self.topline_layout.addWidget(self.btn_save)

        self.tab_settings_layout.addLayout(self.topline_layout)

        self.img_display = QLabel()
        self.img_display.setFixedHeight(600)  # Set fixed height
        self.img_display.setAlignment(QtCore.Qt.AlignCenter)  # Align center
        self.tab_settings_layout.addWidget(self.img_display)

        self.tab_settings.setLayout(self.tab_settings_layout)

        self.btn_roi.clicked.connect(self.select_roi)
        self.btn_save.clicked.connect(self.init_experiment_data)



    def setup_experiment_tab(self):
        self.tab_experiment_layout = QVBoxLayout(self.tab_experiment)

        # Create buttons and place them in a line at the top
        self.btn_plot = QPushButton("Plot")
        self.btn_record = QPushButton("Record")
        self.btn_stop = QPushButton("Stop")

        self.top_button_layout = QHBoxLayout()
        self.top_button_layout.addWidget(self.btn_plot)
        self.top_button_layout.addWidget(self.btn_record)
        self.top_button_layout.addWidget(self.btn_stop)
        # Link buttons to calling specific functions
        self.btn_plot.clicked.connect(self.plotting)
        self.btn_record.clicked.connect(self.recording)
        self.btn_stop.clicked.connect(self.stop)

        self.tab_experiment_layout.addLayout(self.top_button_layout)

        # Create plot widgets
        self.plot1 = pg.PlotWidget()
        self.plot2 = pg.PlotWidget()
        self.plot3 = pg.PlotWidget()
        self.plot4 = pg.PlotWidget()

        self.top_layout = QHBoxLayout()
        self.top_layout.addWidget(self.plot4)

        self.bottom_layout = QHBoxLayout()
        self.bottom_layout.addWidget(self.plot1)
        self.bottom_layout.addWidget(self.plot2)
        self.bottom_layout.addWidget(self.plot3)

        self.tab_experiment_layout.addLayout(self.top_layout)
        self.tab_experiment_layout.addLayout(self.bottom_layout)

        self.tab_experiment.setLayout(self.tab_experiment_layout)

    def init_experiment_data(self):
        experimenter_name = self.txt_name.text()

        if not experimenter_name:
            QMessageBox.critical(self, "Error", "Please enter the experimenter's name")
            return

        folder_name = f"{experimenter_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        folder_path = os.path.join(os.getcwd(), folder_name)

        try:
            os.mkdir(folder_path)
        except OSError:
            QMessageBox.critical(self, "Error", "Failed to create experiment folder")
            return

        self.experiment_data_path = os.path.join(folder_path, "ExperimentData.csv")
        with open(self.experiment_data_path, "w") as file:
            writer = csv.writer(file)
            header = ["Timestamp", "Sum Fluorescence (405nm)", "Sum Fluorescence (470nm)", "Sum Fluorescence (590nm)"]
            writer.writerow(header)

        self.experiment_info_path = os.path.join(folder_path, "ExperimentInfo.csv")
        with open(self.experiment_info_path, "w") as file:
            writer = csv.writer(file)
            header = [
                "Experiment Date and Time",
                "Recording Start Time",
                "Recording End Time",
                "Sampling Rate",
                "Exposure",
                "ROI_XMIN",
                "ROI_XMAX",
                "ROI_YMIN",
                "ROI_YMAX",
                "ROI_XRANGE",
                "ROI_YRANGE",
            ]
            writer.writerow(header)

        self.images_folder_path = os.path.join(folder_path, "images")
        os.mkdir(self.images_folder_path)
        self.is_experiment_initialized
        QMessageBox.information(self, "Success", "New experiment has been successfully initialized.")

    def select_roi(self):
        if self.acquire_image():
            try:
                img = cv2.cvtColor(self.image, cv2.COLOR_BAYER_BG2RGB)
                # img = self.image
                roi = cv2.selectROI(img)
                self.roi = ROI(roi)
                img_crop = img[self.roi.xmin:self.roi.xmax, self.roi.ymin:self.roi.ymax]

                # Convert the OpenCV image to QImage
                q_img = qimage2ndarray.array2qimage(img_crop)

                # Set the QImage in QLabel
                pixmap = QPixmap.fromImage(q_img)
                self.img_display.setPixmap(pixmap)
                if self.roi_xmax > 0 or self.roi_ymax > 0:
                    cv2.destroyAllWindows()
            except:
                cv2.destroyAllWindows()

    def acquire_image(self):
        system = PySpin.System.GetInstance()
        cam_list = system.GetCameras()
        try:
            if cam_list.GetSize() == 0:
                QMessageBox.critical(self, "Error", "No cameras found")
                return False
            else:
                cam = cam_list.GetByIndex(0)
                cam.Init()
                cam.BeginAcquisition()
                image_result = cam.GetNextImage()
                self.image = image_result.GetNDArray()
                image_result.Release()
                cam.EndAcquisition()
                cam.DeInit()
                del cam
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return False
        cam_list.Clear()
        system.ReleaseInstance()
        return True        

    def init_plotting_recording(self):
        # Flags for whether or not the user is plotting and recording
        self.is_plotting = False #self.deque_acq,  deque([]), self.deque_record,deque([]), 
        self.deque_recording, self.deque_plotting =deque([]), deque([])
        self.iterator = 0
        self.t0 = 0

        
        self.acq_worker = FLIRAcquisitionWorker()
        self.rec_worker = RecordingWorker()
        
        # Set labels, colors, ranges for each plot widget
        self.plot1.setLabel("bottom", "Time since start (s)")
        self.plot1.setLabel("left", "Intensity")
        self.plot2.setLabel("bottom", "Time since start (s)")
        self.plot2.setLabel("left", "Intensity")
        self.plot3.setLabel("bottom", "Time since start (s)")
        self.plot3.setLabel("left", "Intensity")
        self.plot4.setLabel("bottom", "Time since start (s)")
        self.plot4.setLabel("left", "Intensity")

        self.pen1 = pg.mkPen(color=(0, 255, 0))
        self.plot1.setYRange(-6,6)
        self.pen2 = pg.mkPen(color=(0, 0, 255))
        self.plot2.setYRange(-6,6)
        self.pen3 = pg.mkPen(color=(255, 0, 255))
        self.plot3.setYRange(-6,6)
        self.pen4 = pg.mkPen(color =(255, 140, 0))
        self.plot4.setYRange(-6,6)

        # Limits the number of data points shown on the graph
        self.graph_lim = 100
        """
        First deque will be used to quickly store time and image data, then 
        the data will be passed into the plot deque, which is used for 
        computation and plotting
        """
        self.deque_timesteps1 = deque([], maxlen=self.graph_lim)
        self.deque_timesteps2 = deque([], maxlen=self.graph_lim)
        self.deque_timesteps3 = deque([], maxlen=self.graph_lim)
        self.deque_sequence1 = deque([], maxlen=self.graph_lim)
        self.deque_sequence2 = deque([], maxlen=self.graph_lim)
        self.deque_sequence3 = deque([], maxlen=self.graph_lim)

    def recording(self):
        if not self.is_plotting:
            QMessageBox.critical(self,
            "Recording Cannot Start",
            "Please begin plotting before recording."
            )
        else:
            # if len(deque_record) == 0:
            #     deque_record.append(1)
            self.rec_worker.start() 
            

    def plotting(self):
        if not self.is_experiment_initialized:
            QMessageBox.critical(self,
            "Plotting Cannot Start",
            "Please initialize the new experiment first."
            )
            return
        # if len(self.deque_acq) == 0:
        #         self.deque_acq.append(1)
        self.acq_worker.start()

        self.plot_timer = QtCore.QTimer()
        self.plot_timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.plot_timer.timeout.connect(self.update_plot)
        self.plot_timer.start(10)
        self.is_plotting = True


    def update_plot(self):
        # Only update if deques are not empty
        if self.deque_plotting:
            t, img = self.deque_plotting.popleft()
            if self.iterator == 0:
                self.t0 = time.perf_counter()
            t = t - self.t0
            img = img[self.roi.xmin:self.roi.xmax, self.roi.ymin:self.roi.ymax]
            if self.iterator % 3 == 0:
                self.deque_timesteps1.append(t)
                self.deque_sequence1.append(np.sum(img))
                mu, std = np.average(self.deque_sequence1), np.std(self.deque_sequence1)
                if std > 0:
                    sequence = (self.deque_sequence1 - mu )/ std
                    self.plot1.plotItem.clear()
                    self.plot1.plotItem.plot(
                        self.deque_timesteps1,
                        sequence,
                        pen=self.pen1,
                    )
            elif self.iterator % 3 == 1:
                self.deque_timesteps2.append(t)
                self.deque_sequence2.append(np.sum(img))
                mu, std = np.average(self.deque_sequence2), np.std(self.deque_sequence2)
                if std > 0:
                    sequence = (self.deque_sequence2 - mu )/ std
                    self.plot2.plotItem.clear()
                    self.plot2.plotItem.plot(
                        self.deque_timesteps2,
                        sequence,
                        pen=self.pen2,
                    )
            else: 
                self.deque_timesteps3.append(t)
                self.deque_sequence3.append(np.sum(img))
                mu, std = np.average(self.deque_sequence3), np.std(self.deque_sequence3)
                if std > 0:
                    sequence = (self.deque_sequence3 - mu )/ std
                    self.plot3.plotItem.clear()
                    self.plot3.plotItem.plot(
                        self.deque_timesteps3,
                        sequence,
                        pen=self.pen3,
                    )
            self.iterator +=1
            if self.iterator > 1 and self.iterator % 3 == 0:
                sequence = (self.deque_sequence1 - self.deque_sequence2)/self.deque_sequence2
                self.plot4.plotItem.clear()
                self.plot4.plotItem.plot(
                    self.deque_timesteps1,
                    sequence,
                    pen=self.pen4,
                )



    def stop(self):
        self.plot_timer.stop()
        self.is_plotting = False
        # self.acq_worker.quit()
        # time.sleep(1)
        # if len(deque_record) > 0:
        #     _ = deque_record.popleft()
        # if len(deque_acq) > 0:
        #     _ = deque_acq.popleft()
        time.sleep(3)
        self.acq_worker.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv) 
    window = MainWindow()
    app.exec_()
