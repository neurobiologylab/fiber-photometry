

from PySide2 import QtCore
from PySide2.QtCore import Signal, QThread, QTimer
from PySide2 import QtGui
from PySide2.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QApplication,
    QPushButton,
    QMessageBox,QGridLayout, QLabel, QLineEdit, QProgressBar, QCheckBox, QLCDNumber
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
from flir import Worker, ROI, FLIR
from widget import MyMplCanvas


# uiclass, baseclass = pg.Qt.loadUiType("main.ui")
# If changes are made in QtDesigner, open cmd in main.ui folder and execute:
# pyside2-uic main.ui -o MainWindow.py
'''
connector 0: ao0 camera, ao1 405 (on labview channels 1,2) 
connector 1: ao0 470, ao1 625 (on labview channels 3,4)
'''

class Main(QMainWindow):
    work_requested = Signal()  
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
        self.chk_record = self.findChild(QCheckBox, "chk_record")
        self.lcd_img = self.findChild(QLCDNumber,"lcd_img")
        self.lcd_time = self.findChild(QLCDNumber,"lcd_time")
        self.btn_stop = self.findChild(QPushButton, "btn_stop")
        self.img_display = self.findChild(QLabel, "img_display")

        self.canvas_chn1 = self.findChild(MyMplCanvas, "canvas_chn1")
        self.canvas_chn2 = self.findChild(MyMplCanvas, "canvas_chn2")
        self.canvas_chn3 = self.findChild(MyMplCanvas, "canvas_chn3")
        self.canvas_list = [self.canvas_chn1, self.canvas_chn2, self.canvas_chn3]

        # Link buttons to ...
        self.btn_exp_init.clicked.connect(self.init_experiment)        
        self.btn_roi.clicked.connect(self.select_roi)
        self.btn_plot.clicked.connect(self.plotting)
        # self.chk_record.clicked.connect(self.recording)
        self.btn_stop.clicked.connect(self.stop)

        # Flag for ....
        self.is_experiment_initialized = False
        self.roi = None           
        self.worker = None  
        self.timer = None    
        self.worker_thread = None

                
        # Set labels, colors, ranges for each plot widget
        # self.plot_chn1.setLabel("bottom", "Time since start (s)")
        # self.plot_chn1.setLabel("left", "Intensity")
        # self.plot_chn2.setLabel("bottom", "Time since start (s)")
        # self.plot_chn2.setLabel("left", "Intensity")
        # self.plot_chn3.setLabel("bottom", "Time since start (s)")
        # self.plot_chn3.setLabel("left", "Intensity")
        # self.plot_final.setLabel("bottom", "Time since start (s)")
        # self.plot_final.setLabel("left", "Intensity")
        # self.plot_final.hide()

        # self.pen1 = mkPen(color=(0, 255, 0))
        # self.plot_chn1.setYRange(-6,6)
        # self.pen2 = mkPen(color=(0, 0, 255))
        # self.plot_chn2.setYRange(-6,6)
        # self.pen3 = mkPen(color=(255, 0, 255))
        # self.plot_chn3.setYRange(-6,6)
        # self.pen4 = mkPen(color =(255, 140, 0))
        # self.plot_final.setYRange(-6,6)

        self.show()
        
    def init_plotting_recording(self):
        # Flags for whether or not the user is plotting and recording
        self.is_plotting = False #self.deque_acq,  deque([]), self.deque_record,deque([]), 
        self.deque_recording, self.deque_plotting =deque([]), deque([])
        self.iterator = 0
        self.t0 = 0
        
        self.canvas_chn1.clear()
        self.canvas_chn2.clear()
        self.canvas_chn3.clear()


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
        flir = FLIR()
        # if flir.cam is None:
        #     QMessageBox.critical(self, "Error", "No Camera Found!")
        #     return
        result, img = flir.take_single_pic(exposure_time=800000.0)
        if result:
            try:
                # img = cv2.cvtColor(img, cv2.COLOR_BAYER_BG2RGB)
                roi = cv2.selectROI(img)
                self.roi = ROI(roi)
                img_crop = img[self.roi.xmin:self.roi.xmax, self.roi.ymin:self.roi.ymax]
                # Convert the OpenCV image to QImage
                q_img = qimage2ndarray.array2qimage(img_crop)
                # Set the QImage in QLabel
                pixmap = QtGui.QPixmap.fromImage(q_img)
                self.img_display.setPixmap(pixmap)
                if self.roi and (self.roi.xmax > 0 or self.roi.ymax > 0):
                    cv2.destroyAllWindows()
            except:
                cv2.destroyAllWindows()
        else:
            QMessageBox.critical(self, "Error", "No camera found! Please ensure the camera is connected and powered on.")

    # def configure_exposure(self, cam):
    #     try:
    #         result = True
    #         if cam.ExposureAuto.GetAccessMode() != PySpin.RW:
    #             print('Unable to disable automatic exposure. Aborting...')
    #             return False

    #         cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
            
    #         # Set exposure time manually; exposure time recorded in microseconds

    #         if cam.ExposureTime.GetAccessMode() != PySpin.RW:
    #             print('Unable to set exposure time. Aborting...')
    #             return False

    #         # Ensure desired exposure time does not exceed the maximum
    #         exposure_time_to_set = 800000.0
    #         exposure_time_to_set = min(cam.ExposureTime.GetMax(), exposure_time_to_set)
    #         cam.ExposureTime.SetValue(exposure_time_to_set)
            
    #     except PySpin.SpinnakerException as ex:
    #         print('Error: %s' % ex)
    #         result = False

    #     return result

    # def acquire_images(self, cam, nodemap, nodemap_tldevice):

    #     try:
    #         result = True
    #         node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
    #         if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
    #             print('Unable to set acquisition mode to continuous (enum retrieval). Aborting...')
    #             return False

    #         node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
    #         if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(node_acquisition_mode_continuous):
    #             print('Unable to set acquisition mode to continuous (entry retrieval). Aborting...')
    #             return False

    #         acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()

    #         node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

    #         cam.BeginAcquisition()

    #         try:
    #             image_result = cam.GetNextImage(30000)

    #             if image_result.IsIncomplete():
    #                 print('Image incomplete with image status %d ...' % image_result.GetImageStatus())

    #             else:
    #                 img = image_result.Convert(PySpin.PixelFormat_Mono8, PySpin.HQ_LINEAR)
    #                 self.image = np.array(img.GetData(), dtype="uint8").reshape((img.GetHeight(), img.GetWidth()))
    #                 image_result.Release()

    #         except PySpin.SpinnakerException as ex:
    #             print('Error: %s' % ex)
    #             return False

    #         cam.EndAcquisition()
        
    #     except PySpin.SpinnakerException as ex:
    #         print('Error: %s' % ex)
    #         return False

    #     return result

    # def reset_exposure(self, cam):
    #     try:
    #         result = True
    #         if cam.ExposureAuto.GetAccessMode() != PySpin.RW:
    #             print('Unable to enable automatic exposure (node retrieval). Non-fatal error...')
    #             return False

    #         cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Continuous)

    #     except PySpin.SpinnakerException as ex:
    #         print('Error: %s' % ex)
    #         result = False

    #     return result

    # def run_single_camera(self, cam):
    #     try:
    #         result = True
    #         nodemap_tldevice = cam.GetTLDeviceNodeMap()
    #         cam.Init()
    #         nodemap = cam.GetNodeMap()

    #         if self.configure_exposure(cam) is False:
    #             return False
    
    #         result &= self.acquire_images(cam, nodemap, nodemap_tldevice)

    #         result &= self.reset_exposure(cam)

    #         cam.DeInit()

    #     except PySpin.SpinnakerException as ex:
    #         print('Error: %s. Camera might be in use or not accessible.' % ex)  
    #         result = False
        
    #     # if not result:
    #     #     try:
    #     #         cam.EndAcquisition()
    #     #         print("Camera ended acquisition.")
    #     #     except PySpin.SpinnakerException as ex:
    #     #         print('Error: %s. Failed to end acquisition.' % ex)

    #     #     try:
    #     #         cam.DeInit()
    #     #         print("Camera de-initialized.")
    #     #     except PySpin.SpinnakerException as ex:
    #     #         print('Error: %s. Failed to de-initialize the camera.' % ex)

    #     return result

    # def get_img(self):
    #     result = True
        
    #     system = PySpin.System.GetInstance()
        
    #     cam_list = system.GetCameras()
    #     cam = cam_list[0]

    #     result &= self.run_single_camera(cam)

    #     del cam
    #     cam_list.Clear()
    #     system.ReleaseInstance()

    #     return result

    def disable_all_buttons(self):    
        self.btn_roi.setEnabled(False)        
        self.btn_exp_init.setEnabled(False)           
        self.btn_plot.setEnabled(False)        
        self.chk_record.setEnabled(False)   

    def enable_all_buttons(self):    
        self.btn_roi.setEnabled(True)        
        self.btn_exp_init.setEnabled(True)           
        self.btn_plot.setEnabled(True)        
        self.chk_record.setEnabled(True)          
            
    def plotting(self):
        if not self.is_experiment_initialized:
            QMessageBox.critical(self,
            "Plotting Cannot Start",
            "Please initialize a new experiment first."
            )
            return
        self.disable_all_buttons()       
        self.worker = Worker(self.roi, images_folder_path= self.images_folder_path, images_save = self.chk_record.isChecked())
        self.worker_thread = QThread()
        self.worker.num_imgs.connect(self.update_num_imgs)
        self.worker.num_seconds.connect(self.update_num_seconds)
        self.worker.completed.connect(self.complete)
        self.work_requested.connect(self.worker.do_work)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start() 
        # self.recording_requested.emit(True)
        self.worker.set_running(True)
        self.work_requested.emit()

        self.update_canvas()
    
    def update_canvas(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.realtime_signal)
        self.timer.start(10)

    def realtime_signal(self):
        for i, ds in enumerate(self.worker.image_acquisition):
            print(f"image_acquisition {i}")
            if len(ds['mean'])>0:
                self.canvas_list[i].plot(ds['mean'][-150:], ds['time'][-150:])  

    def stop(self):
        # self.recording_requested.emit(False)        
        self.worker.set_running(False)

    def update_num_imgs(self,n):
        self.lcd_img.display(n)

    def update_num_seconds(self,n):
        self.lcd_time.display(n)

    def complete(self,v):
        if v:
            print("Completed!")      
        if self.timer:
            self.timer.stop()
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()

        # self.is_plotting = False
        # self.acq_worker.quit()
        dic = {'chn1_time':self.worker.image_acquisition[0]["time"], 'chn1_avg_intensity':self.worker.image_acquisition[0]["mean"],'chn2_time':self.worker.image_acquisition[1]["time"], 'chn2_avg_intensity':self.worker.image_acquisition[1]["mean"],'chn3_time': self.worker.image_acquisition[2]["time"],'chn3_avg_intensity':self.worker.image_acquisition[2]["mean"]}

        dic_len = min(len(dic['chn1_time']),len(dic['chn2_time']),len(dic['chn3_time']))
        dic['chn1_time'], dic['chn1_avg_intensity'] = dic['chn1_time'][:dic_len], dic['chn1_avg_intensity'][:dic_len]
        dic['chn2_time'], dic['chn2_avg_intensity'] = dic['chn2_time'][:dic_len], dic['chn2_avg_intensity'][:dic_len]
        dic['chn3_time'], dic['chn3_avg_intensity'] = dic['chn3_time'][:dic_len], dic['chn3_avg_intensity'][:dic_len]
        df_data = pd.DataFrame(dic).astype({'chn1_avg_intensity': 'float','chn2_avg_intensity': 'float','chn3_avg_intensity': 'float'})
        df_data.to_csv(self.experiment_data_path)
        # if self.rec_worker:
        #     self.rec_worker.is_running = False  
        #     time.sleep(3) 
        #     print(self.rec_worker.isRunning())
        #     self.rec_worker.quit() 
        # if self.acq_worker:    
        #     self.acq_worker.is_running = False
        #     time.sleep(3) 
        #     print(self.acq_worker.isRunning())
        #     self.acq_worker.quit()                
        self.is_experiment_initialized = False     
        self.enable_all_buttons() 
        QMessageBox.information(self, "Success", f"Experiment data has been saved at {self.experiment_data_path}.")




if __name__ == "__main__":
    app = QApplication(sys.argv)
    UIWindow = Main()
    app.exec_()