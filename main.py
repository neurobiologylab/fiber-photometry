

from PySide2.QtCore import Signal, QThread, QTimer
from PySide2 import QtGui
from PySide2.QtWidgets import (
    QMainWindow,
    QApplication,
    QPushButton,
    QMessageBox, QLabel, QLineEdit, QCheckBox, QLCDNumber
)
from main_ui import MainUI
import os
import cv2
import pandas as pd
import datetime
import os
import qimage2ndarray
from flir import Worker, ROI, FLIR
from widget import MyMplCanvas



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
        self.lcd_freq = self.findChild(QLCDNumber,"lcd_freq")
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

        self.show()
        
    def init_plotting_recording(self):
        
        self.canvas_chn1.clear()
        self.canvas_chn2.clear()
        self.canvas_chn3.clear()


        # Limits the number of data points shown on the graph
        self.graph_lim = 100
        self.lcd_freq.display(0)
        self.lcd_time.display(0)


    def init_experiment(self):
        animal_name = self.txt_name.text()   
         
        if not animal_name:
            QMessageBox.critical(self, "Error", "Please enter the experimenter's name")
            return
        
        if self.roi is None:
            QMessageBox.critical(self, "Error", "Please select the region of interest")
            return

        folder_name = f"{animal_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
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
        # Opt for a lower exposure time when a high image acquisition frequency is selected, to prevent motion blur and ensure adequate frame capture rate.
        self.worker = Worker(self.roi, images_folder_path= self.images_folder_path, images_save = self.chk_record.isChecked(), exposure_time = 30000.0)
        self.worker_thread = QThread()
        self.worker.frequency.connect(self.update_frequency)
        self.worker.elapsed_time.connect(self.update_elapsed_time)
        self.worker.completed.connect(self.complete)
        self.work_requested.connect(self.worker.do_work)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start() 
        self.worker.set_running(True)
        self.work_requested.emit()

        self.update_canvas()
    
    def update_canvas(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.realtime_signal)
        self.timer.start(10)

    def realtime_signal(self):
        for i, ds in enumerate(self.worker.image_acquisition):
            if len(ds['mean'])>0:
                self.canvas_list[i].plot(ds['mean'][-150:], ds['time'][-150:])  

    def stop(self):     
        self.worker.set_running(False)

    def update_frequency(self,n):
        self.lcd_freq.display(n)

    def update_elapsed_time(self,n):
        self.lcd_time.display(n)

    def complete(self,v):
        if v:
            print("Completed!")      
        if self.timer:
            self.timer.stop()
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()

        dic = {'chn1_time':self.worker.image_acquisition[0]["time"], 'chn1_avg_intensity':self.worker.image_acquisition[0]["mean"],'chn2_time':self.worker.image_acquisition[1]["time"], 'chn2_avg_intensity':self.worker.image_acquisition[1]["mean"],'chn3_time': self.worker.image_acquisition[2]["time"],'chn3_avg_intensity':self.worker.image_acquisition[2]["mean"]}

        dic_len = min(len(dic['chn1_time']),len(dic['chn2_time']),len(dic['chn3_time']))
        dic['chn1_time'], dic['chn1_avg_intensity'] = dic['chn1_time'][:dic_len], dic['chn1_avg_intensity'][:dic_len]
        dic['chn2_time'], dic['chn2_avg_intensity'] = dic['chn2_time'][:dic_len], dic['chn2_avg_intensity'][:dic_len]
        dic['chn3_time'], dic['chn3_avg_intensity'] = dic['chn3_time'][:dic_len], dic['chn3_avg_intensity'][:dic_len]
        df_data = pd.DataFrame(dic).astype({'chn1_avg_intensity': 'float','chn2_avg_intensity': 'float','chn3_avg_intensity': 'float'})
        df_data.to_csv(self.experiment_data_path)              
        self.is_experiment_initialized = False     
        self.enable_all_buttons() 
        QMessageBox.information(self, "Success", f"Experiment data has been saved at {self.experiment_data_path}.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    UIWindow = Main()
    app.exec_()