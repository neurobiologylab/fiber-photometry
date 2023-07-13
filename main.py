

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QApplication,
    QPushButton,
    QMessageBox,QGridLayout, QLabel, QLineEdit
)
from pyqtgraph import PlotWidget, mkPen
from main_ui import MainUI
import sys
import pyqtgraph as pg
import cv2
import numpy as np
import pandas as pd
from collections import deque
import time
import datetime
import os
import csv
import PySpin
from PIL import Image
import qimage2ndarray
# import pyqtgraph as pg
from scipy.stats import zscore
import nidaqmx
from nidaqmx.constants import AcquisitionType
from pathlib import Path, PureWindowsPath
# from parameter_window import ParameterWindow
# from experiment_setup import Settings
from flir import RecordingWorker, FLIRAcquisitionWorker, ROI


# uiclass, baseclass = pg.Qt.loadUiType("main.ui")
# If changes are made in QtDesigner, open cmd in main.ui folder and execute:
# pyside2-uic main.ui -o MainWindow.py
'''
connector 0: ao0 camera, ao1 405 (on labview channels 1,2) 
connector 1: ao0 470, ao1 625 (on labview channels 3,4)
'''

class Main(QMainWindow):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent=parent)
        ui = MainUI()
        ui.setupUi(self)

        # Customize title and icon in window corner
        self.setWindowTitle("NBI Photometry")
        self.setWindowIcon(QtGui.QIcon('nbi-logo.jpg'))

        # .....
        self.txt_name = self.findChild(QLineEdit,"txt_name")
        self.btn_roi = self.findChild(QPushButton, "btn_roi")
        self.btn_exp_init = self.findChild(QPushButton, "btn_exp_init")        
        self.btn_plot = self.findChild(QPushButton, "btn_plot")
        self.btn_record = self.findChild(QPushButton, "btn_record")
        self.btn_stop = self.findChild(QPushButton, "btn_stop")
        self.img_display = self.findChild(QLabel, "img_display")

        self.plot_final = self.findChild(PlotWidget, "plot_final")
        self.plot_chn1 = self.findChild(PlotWidget, "plot_chn1")
        self.plot_chn2 = self.findChild(PlotWidget, "plot_chn2")
        self.plot_chn3 = self.findChild(PlotWidget, "plot_chn3")


        # Link buttons to ...
        self.btn_exp_init.clicked.connect(self.init_experiment)        
        self.btn_roi.clicked.connect(self.select_roi)
        self.btn_plot.clicked.connect(self.plotting)
        self.btn_record.clicked.connect(self.recording)
        self.btn_stop.clicked.connect(self.stop)

        # Flag for ....
        self.is_experiment_initialized = False
        self.roi = None         
        self.rec_worker = None        
        self.acq_worker = None  
        self.plot_timer = None
                
        # Set labels, colors, ranges for each plot widget
        self.plot_chn1.setLabel("bottom", "Time since start (s)")
        self.plot_chn1.setLabel("left", "Intensity")
        self.plot_chn2.setLabel("bottom", "Time since start (s)")
        self.plot_chn2.setLabel("left", "Intensity")
        self.plot_chn3.setLabel("bottom", "Time since start (s)")
        self.plot_chn3.setLabel("left", "Intensity")
        self.plot_final.setLabel("bottom", "Time since start (s)")
        self.plot_final.setLabel("left", "Intensity")
        self.plot_final.hide()

        self.pen1 = mkPen(color=(0, 255, 0))
        self.plot_chn1.setYRange(-6,6)
        self.pen2 = mkPen(color=(0, 0, 255))
        self.plot_chn2.setYRange(-6,6)
        self.pen3 = mkPen(color=(255, 0, 255))
        self.plot_chn3.setYRange(-6,6)
        self.pen4 = mkPen(color =(255, 140, 0))
        self.plot_final.setYRange(-6,6)

        self.show()
        
    def init_plotting_recording(self):
        # Flags for whether or not the user is plotting and recording
        self.is_plotting = False #self.deque_acq,  deque([]), self.deque_record,deque([]), 
        self.deque_recording, self.deque_plotting =deque([]), deque([])
        self.iterator = 0
        self.t0 = 0
        
        self.plot_chn1.clear()
        self.plot_chn2.clear()
        self.plot_chn3.clear()
        self.plot_final.clear()


        # Limits the number of data points shown on the graph
        self.graph_lim = 100
        """
        First deque will be used to quickly store time and image data, then 
        the data will be passed into the plot deque, which is used for 
        computation and plotting
        """
        # self.deque_timesteps1 = deque([], maxlen=self.graph_lim)
        # self.deque_timesteps2 = deque([], maxlen=self.graph_lim)
        # self.deque_timesteps3 = deque([], maxlen=self.graph_lim)
        # self.deque_sequence1 = deque([], maxlen=self.graph_lim)
        # self.deque_sequence2 = deque([], maxlen=self.graph_lim)
        # self.deque_sequence3 = deque([], maxlen=self.graph_lim)
        self.timesteps1 = np.empty(0)
        self.timesteps2 = np.empty(0)
        self.timesteps3 = np.empty(0)
        self.siginal1 = np.empty(0)
        self.siginal2 = np.empty(0)
        self.siginal3 = np.empty(0)


    def init_experiment(self):
        experimenter_name = self.txt_name.text()   
         
        if not experimenter_name:
            QMessageBox.critical(self, "Error", "Please enter the experimenter's name")
            return
        
        if self.roi is None:
            QMessageBox.critical(self, "Error", "Please select the region of interest")
            return

        folder_name = f"{experimenter_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        folder_path = os.path.join(os.getcwd(), "data", folder_name)

        try:
            os.mkdir(folder_path)
        except OSError:
            QMessageBox.critical(self, "Error", "Failed to create experiment folder")
            return

        self.experiment_data_path = os.path.join(folder_path, "ExperimentData.csv")
        self.images_folder_path = os.path.join(folder_path, "images")
        os.mkdir(self.images_folder_path)        
        self.init_plotting_recording()
        self.is_experiment_initialized = True
        QMessageBox.information(self, "Success", "A new experiment has been successfully initialized.")

    def select_roi(self):
        if self.get_img():
            try:
                img = cv2.cvtColor(self.image, cv2.COLOR_BAYER_BG2RGB)
                roi = cv2.selectROI(img)
                self.roi = ROI(roi)
                img_crop = img[self.roi.xmin:self.roi.xmax, self.roi.ymin:self.roi.ymax]
                # Convert the OpenCV image to QImage
                q_img = qimage2ndarray.array2qimage(img_crop)
                # Set the QImage in QLabel
                pixmap = QtGui.QPixmap.fromImage(q_img)
                self.img_display.setPixmap(pixmap)
                if self.roi_xmax > 0 or self.roi_ymax > 0:
                    cv2.destroyAllWindows()
            except:
                cv2.destroyAllWindows()

    def configure_exposure(self, cam):
        try:
            result = True
            if cam.ExposureAuto.GetAccessMode() != PySpin.RW:
                print('Unable to disable automatic exposure. Aborting...')
                return False

            cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
            
            # Set exposure time manually; exposure time recorded in microseconds

            if cam.ExposureTime.GetAccessMode() != PySpin.RW:
                print('Unable to set exposure time. Aborting...')
                return False

            # Ensure desired exposure time does not exceed the maximum
            exposure_time_to_set = 800000.0
            exposure_time_to_set = min(cam.ExposureTime.GetMax(), exposure_time_to_set)
            cam.ExposureTime.SetValue(exposure_time_to_set)
            
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False

        return result

    def acquire_images(self, cam, nodemap, nodemap_tldevice):

        try:
            result = True
            node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
            if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
                print('Unable to set acquisition mode to continuous (enum retrieval). Aborting...')
                return False

            node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
            if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(node_acquisition_mode_continuous):
                print('Unable to set acquisition mode to continuous (entry retrieval). Aborting...')
                return False

            acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()

            node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

            cam.BeginAcquisition()

            try:
                image_result = cam.GetNextImage(30000)

                if image_result.IsIncomplete():
                    print('Image incomplete with image status %d ...' % image_result.GetImageStatus())

                else:
                    img = image_result.Convert(PySpin.PixelFormat_Mono8, PySpin.HQ_LINEAR)
                    self.image = np.array(img.GetData(), dtype="uint8").reshape((img.GetHeight(), img.GetWidth()))
                    image_result.Release()

            except PySpin.SpinnakerException as ex:
                print('Error: %s' % ex)
                return False

            cam.EndAcquisition()
        
        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return False

        return result

    def reset_exposure(self, cam):
        try:
            result = True
            if cam.ExposureAuto.GetAccessMode() != PySpin.RW:
                print('Unable to enable automatic exposure (node retrieval). Non-fatal error...')
                return False

            cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Continuous)

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False

        return result

    def run_single_camera(self, cam):
        try:
            result = True
            nodemap_tldevice = cam.GetTLDeviceNodeMap()
            cam.Init()
            nodemap = cam.GetNodeMap()

            if self.configure_exposure(cam) is False:
                return False
    
            result &= self.acquire_images(cam, nodemap, nodemap_tldevice)

            result &= self.reset_exposure(cam)

            cam.DeInit()

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False

        return result


    def get_img(self):
        result = True
        
        system = PySpin.System.GetInstance()
        
        cam_list = system.GetCameras()
        cam = cam_list[0]
        result &= self.run_single_camera(cam)

        del cam
        cam_list.Clear()
        system.ReleaseInstance()

        return result

    def recording(self):
        if not self.is_plotting:
            QMessageBox.critical(self,
            "Recording Cannot Start",
            "Please begin plotting before recording."
            )
        else:
            # if len(deque_record) == 0:
            #     deque_record.append(1)
            self.rec_worker = RecordingWorker(self.deque_recording, self.roi, images_folder_path= self.images_folder_path)
            self.rec_worker.is_running = True
            self.rec_worker.start() 
            
    def plotting(self):
        if not self.is_experiment_initialized:
            QMessageBox.critical(self,
            "Plotting Cannot Start",
            "Please initialize a new experiment first."
            )
            return
        self.acq_worker = FLIRAcquisitionWorker(self.deque_recording, self.deque_plotting )
        self.acq_worker.is_running = True        
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
                self.timesteps1 = np.append(self.timesteps1, t)
                self.siginal1 = np.append(self.siginal1, np.mean(img))
                mu, std = np.average(self.siginal1), np.std(self.siginal1)
                if std > 0:
                    sequence = (self.siginal1 - mu )/ std
                    self.plot_chn1.plotItem.clear()
                    self.plot_chn1.plotItem.plot(
                        self.timesteps1[-self.graph_lim:],
                        sequence[-self.graph_lim:],
                        pen=self.pen1,
                    )
            elif self.iterator % 3 == 1:
                self.timesteps2 = np.append(self.timesteps2, t)
                self.siginal2 = np.append(self.siginal2, np.mean(img))
                mu, std = np.average(self.siginal2), np.std(self.siginal2)
                if std > 0:
                    sequence = (self.siginal2 - mu )/ std
                    self.plot_chn2.plotItem.clear()
                    self.plot_chn2.plotItem.plot(
                        self.timesteps2[-self.graph_lim:],
                        sequence[-self.graph_lim:],
                        pen=self.pen2,
                    )
            else: 
                self.timesteps3 = np.append(self.timesteps3, t)
                self.siginal3 = np.append(self.siginal3, np.mean(img))
                mu, std = np.average(self.siginal3), np.std(self.siginal3)
                if std > 0:
                    sequence = (self.siginal3 - mu )/ std
                    self.plot_chn3.plotItem.clear()
                    self.plot_chn3.plotItem.plot(
                        self.timesteps3[-self.graph_lim:],
                        sequence[-self.graph_lim:],
                        pen=self.pen3,
                    )
            self.iterator +=1
            # if self.iterator > 1 and self.iterator % 3 == 0:
            #     sequence = (self.deque_sequence1 - self.deque_sequence2)/self.deque_sequence2
            #     self.plot_final.plotItem.clear()
            #     self.plot_final.plotItem.plot(
            #         self.deque_timesteps1,
            #         sequence,
            #         pen=self.pen4,
            #     )

    def stop(self):
        if self.plot_timer:
            self.plot_timer.stop()
        self.is_plotting = False
        # self.acq_worker.quit()
        dic = {'chn1_time':self.timesteps1, 'chn1_avg_intensity':self.siginal1,'chn2_time':self.timesteps2, 'chn2_avg_intensity':self.siginal2,'chn3_time': self.timesteps3,'chn3_avg_intensity':self.siginal3}

        dic_len = min(len(dic['chn1_time']),len(dic['chn2_time']),len(dic['chn3_time']))
        dic['chn1_time'], dic['chn1_avg_intensity'] = dic['chn1_time'][:dic_len], dic['chn1_avg_intensity'][:dic_len]
        dic['chn2_time'], dic['chn2_avg_intensity'] = dic['chn2_time'][:dic_len], dic['chn2_avg_intensity'][:dic_len]
        dic['chn3_time'], dic['chn3_avg_intensity'] = dic['chn3_time'][:dic_len], dic['chn3_avg_intensity'][:dic_len]
        df_data = pd.DataFrame(dic).astype({'chn1_avg_intensity': 'float','chn2_avg_intensity': 'float','chn3_avg_intensity': 'float'})
        df_data.to_csv(self.experiment_data_path)
        time.sleep(3)
        if self.rec_worker:
            self.rec_worker.is_running = False  
            time.sleep(10) 
            print(self.rec_worker.isRunning())
            self.rec_worker.quit() 
        if self.acq_worker:    
            self.acq_worker.is_running = False
            time.sleep(50) 
            print(self.acq_worker.isRunning())
            self.acq_worker.quit()                
        self.is_experiment_initialized = False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    UIWindow = Main()
    app.exec_()