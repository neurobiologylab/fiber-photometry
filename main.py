

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QApplication,
    QPushButton,
    QMessageBox,
)
from pyqtgraph import PlotWidget
from MainWindow import Ui_MainWindow
import sys
import pyqtgraph as pg
import numpy as np
from collections import deque
import time
import datetime
import os
import csv
import PySpin
from PIL import Image
from scipy.stats import zscore
import nidaqmx
from nidaqmx.constants import AcquisitionType
from pathlib import Path, PureWindowsPath
# from parameter_window import ParameterWindow
from parameter_window import ParameterWindow


uiclass, baseclass = pg.Qt.loadUiType("main.ui")
# If changes are made in QtDesigner, open cmd in main.ui folder and execute:
# pyside2-uic main.ui -o MainWindow.py
#connector 0: ao0 camera, ao1 405 (on labview channels 1,2) 
#connector 1: ao0 470, ao1 625 (on labview channels 3,4)

class GUI(QMainWindow):
    def __init__(self, parent=None):
        super(GUI, self).__init__(parent=parent)
        ui = Ui_MainWindow()
        ui.setupUi(self)

        # Customize title and icon in window corner
        self.setWindowTitle("NBI App")
        self.setWindowIcon(QtGui.QIcon('icon.png'))

        # Pull widgets from the ui file and define them
        self.new_btn = self.findChild(QPushButton, "NewButton")
        self.set_parameters_btn = self.findChild(
            QPushButton, "SetParametersButton"
        )
        self.plot_btn = self.findChild(QPushButton, "PlotButton")
        self.record_btn = self.findChild(QPushButton, "RecordButton")
        self.stop_btn = self.findChild(QPushButton, "StopButton")

        # Link buttons to calling specific functions
        self.new_btn.clicked.connect(self.new)
        self.set_parameters_btn.clicked.connect(self.set_parameters)
        self.plot_btn.clicked.connect(self.plot)
        self.record_btn.clicked.connect(self.record)
        self.stop_btn.clicked.connect(self.stop)

        # Flag for showing user has selected path for new experiment data
        self.path_selected = False
        # Flags for whether or not the user is plotting and recording
        self.is_plotting = False 
        # Initiate double ended queues, store globally so they can be accessed between classes
        global record_deque, acq_deque
        record_deque = deque([])
        acq_deque = deque([])
        self.iterator = 0
        global img_deque, img_plot_deque
        img_deque = deque([])
        img_plot_deque = deque([])
        self.t0 = 0

        # Program time elapsed as a timestamp for each alternating frame
        self.timestamp0 = time.perf_counter()
        self.timestamp1 = time.perf_counter()
        self.timestamp2 = time.perf_counter()
        # Limits the number of data points shown on the graph
        self.graph_lim = 100
        # Create numpy arrays which will contain image data
        self.img_470 = np.array([])
        self.img_405 = np.array([])
        self.img_590 = np.array([])
        # Use deque to store data, fast with threadsafe append and popleft
        self.deque_timestamp0 = deque([])
        self.deque_timestamp1 = deque([])
        self.deque_timestamp2 = deque([])
        self.deque_sum_470 = deque([])
        self.deque_sum_405 = deque([])
        self.deque_sum_590 = deque([])
        """
        First deque will be used to quickly store time and image data, then 
        the data will be passed into the plot deque, which is used for 
        computation and plotting
        """
        self.deque_plot_timestamp_405 = deque([], maxlen=self.graph_lim)
        self.deque_plot_timestamp_470 = deque([], maxlen=self.graph_lim)
        self.deque_plot_timestamp_590 = deque([], maxlen=self.graph_lim)
        self.deque_plot_470 = deque([], maxlen=self.graph_lim)
        self.deque_plot_405 = deque([], maxlen=self.graph_lim)
        self.deque_plot_590 = deque([], maxlen=self.graph_lim)

        # Get pyqtgraph plot widgets from main window and set labels
        # Top plot
        self.plot_filtered_signal = self.findChild(PlotWidget, "PlotView")
        x1_axis = self.plot_filtered_signal.getAxis("bottom")
        x1_axis.setLabel(text="Time since start (s)")
        y1_axis = self.plot_filtered_signal.getAxis("left")
        y1_axis.setLabel(text="Intensity")
        # self.plot_filtered_signal.setYRange(-5,5)
        self.plot_filtered_signal.setYRange(-6,6)

        # Set plot line color to green
        self.pen_filtered_signal = pg.mkPen(color=(0, 255, 0))

        # Bottom left plot
        self.plot_470 = self.findChild(PlotWidget, "PlotView_2")
        x2_axis = self.plot_470.getAxis("bottom")
        x2_axis.setLabel(text="Time since start (s)")
        y2_axis = self.plot_470.getAxis("left")
        y2_axis.setLabel(text="Intensity")
        # Set plot line color to blue
        self.pen_470 = pg.mkPen(color=(0, 0, 255))
        self.plot_470.setYRange(-6,6)

        # Bottom right plot
        self.plot_405 = self.findChild(PlotWidget, "PlotView_3")
        x3_axis = self.plot_405.getAxis("bottom")
        x3_axis.setLabel(text="Time since start (s)")
        y3_axis = self.plot_405.getAxis("left")
        y3_axis.setLabel(text="Intensity")
        # Set plot line color to purple
        self.pen_405 = pg.mkPen(color=(255, 0, 255))
        self.plot_405.setYRange(-6,6)

        #third plot

        self.plot_590 = self.findChild(PlotWidget, "PlotView_4")
        x4_axis = self.plot_590.getAxis("bottom")
        x4_axis.setLabel(text = "Time since start (s)")
        y4_axis = self.plot_590.getAxis("left")
        y4_axis.setLabel(text = "Z-score")
        #set plot line color to orange
        self.pen_590 = pg.mkPen(color =(255, 140, 0))
        self.plot_590.setYRange(-6,6)


        self.show()

    def signal_identify(self, s1, s2, s3, t1, t2, t3):
        # Calculate the mean values of s1, s2, and s3
        mean_values = [sum(l) / len(l) for l in [s1, s2, s3]]

        # Combine the lists using zip
        combined_data = list(zip(mean_values, [s1, s2, s3], [t1, t2, t3]))

        # Sort the combined data based on the mean values
        sorted_data = sorted(combined_data, key=lambda x: x[0])

        # Separate the sorted data into individual lists
        sorted_mean_values, sorted_sequences, sorted_times = zip(*sorted_data)
        return sorted_sequences, sorted_times

    def update_plot(self):
        # Only update if deques are not empty
        if img_plot_deque:
            if self.iterator == 0:
                self.t0 = time.perf_counter()
            t, img = img_plot_deque.popleft()
            t = t - self.t0
            img = img[self.ui.roi_xmin:self.ui.roi_xmax, self.ui.roi_ymin:self.ui.roi_ymax]
            if self.iterator % 3 == 0:
                self.deque_plot_timestamp_405.append(t)
                self.deque_plot_405.append(np.sum(img))
                # Calculate mean (mu) and standard deviation (std)
                self.mu_405 = np.average(self.deque_plot_405)
                # self.std_405 = np.std(self.deque_plot_405)
                # Normalize the data (first std is zero, just ignore the error)
                # if self.std_405 > 0:
                #     self.norm_plot_405 = (
                #         self.deque_plot_405 - self.mu_405
                #     ) / self.std_405 
            elif self.iterator % 3 == 1:
                self.deque_plot_timestamp_470.append(t)
                self.deque_plot_470.append(np.sum(img))
                self.mu_470 = np.average(self.deque_plot_470)
                # self.std_470 = np.std(self.deque_plot_470)
                # if self.std_470 > 0:
                #     self.norm_plot_470 = (
                #         self.deque_plot_470 - self.mu_470
                #     ) / self.std_470
            else: #self.iterator % 3 = 2
                self.deque_plot_timestamp_590.append(t)
                self.deque_plot_590.append(np.average(img))
                # self.mu_590 = np.average(self.deque_plot_590)
                # self.std_590 = np.std(self.deque_plot_590)
                # if self.std_590 > 0:
                #     self.norm_plot_590 = (
                #         self.deque_plot_590 - self.mu_590
                #     )/self.std_590
            dic = {"time_405":[],"time_470":[],"time_590":[],"intensity_405":[],"intensity_470":[],"intensity_590":[]}
            [dic["intensity_590"],dic["intensity_405"],dic["intensity_470"]],[dic["time_590"],dic["time_405"],dic["time_470"]] = self.signal_identify(self.deque_plot_405,self.deque_plot_470,self.deque_plot_590,self.deque_plot_timestamp_405,self.deque_plot_timestamp_470,self.deque_plot_timestamp_590)
    
            # Clear the data from the previous update off of the plot
            self.plot_405.plotItem.clear()
            # Plot the data
            self.plot_405.plotItem.plot(
                dic['time_405'],
                dic['intensity_405'],
                pen=self.pen_405,
            )
            self.plot_470.plotItem.clear()
            self.plot_470.plotItem.plot(
                dic['time_470'],
                dic['intensity_470'],
                pen=self.pen_470,
            )
            self.plot_590.plotItem.clear()
            self.plot_590.plotItem.plot(
                dic['time_590'],
                dic['intensity_590'],
                pen = self.pen_590,
            )
            self.iterator +=1
            if self.iterator > 1 and self.iterator % 3 == 0:
                self.plot_filtered_signal.plotItem.clear()
                # Filter out noise from 470 signal by subtracting 405 signal                
                calibrated_470 = dic['intensity_470'] - dic['intensity_405']
                self.filtered_signal  = zscore(calibrated_470)
                self.plot_filtered_signal.plotItem.plot(
                    dic['time_405'],
                    self.filtered_signal,
                    pen=self.pen_filtered_signal,
                )


    def new(self):
        user_folder = QFileDialog.getExistingDirectory(
            self, "Open a folder:", os.path.expanduser("~")
        )
        self.path = user_folder
        if self.path:
            while len(os.listdir(self.path)) > 0:
                QMessageBox.critical(
                    self,
                    "Invalid Folder Selection",
                    "Please select an empty folder",
                )
                self.new()
            if self.path != "" and os.name == "nt":
                self.path = PureWindowsPath(self.path)
            if self.path != "":
                self.img_path = Path(self.path) / "Images"
                os.mkdir(self.img_path)
                csv_data_name = (
                    "ExperimentData_" + str(datetime.date.today()) + ".csv"
                )
                global rec_csv_data_path
                rec_csv_data_path = Path(self.path) / csv_data_name
                self.csv_data_path = Path(self.path) / csv_data_name
                with open(self.csv_data_path, "w") as file:
                    writer = csv.writer(file)
                    header = [
                        "Timestamp",
                        "Sum Fluoresence (405nm)",
                        "Sum Fluoresence (470nm)",
                        "Sum Fluoresence (590nm)"
                    ]
                    writer.writerow(header)
                csv_info_name = (
                    "ExperimentInfo_" + str(datetime.date.today()) + ".csv"
                )
                self.csv_info_path = Path(self.path) / csv_info_name
                with open(self.csv_info_path, "w") as file:
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
                self.path_selected = True

    def set_parameters(self):
        # Open separate window for choosing image parameters
        self.window = QMainWindow()
        self.ui = ParameterWindow()
        self.window.show()

    def plot(self):
        try: 
            global roi_xmin, roi_xmax, roi_ymin, roi_ymax
            roi_xmin,roi_xmax,roi_ymin,roi_ymax = self.ui.roi_xmin,self.ui.roi_xmax,self.ui.roi_ymin,self.ui.roi_ymax
            # print(roi_xmin,roi_xmax,roi_ymin,roi_ymax)
        except:
            QMessageBox.critical(self,
            "Plotting Cannot Start",
            "Please select parameters before plotting."
            )
            return
        if len(acq_deque) == 0:
                acq_deque.append(1)
        self.acq_worker = FLIRAcquisitionWorker()
        self.acq_worker.start()

        self.plot_timer = QtCore.QTimer()
        self.plot_timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.plot_timer.timeout.connect(self.update_plot)
        self.plot_timer.start(10)

        self.is_plotting = True

    def record(self):
        if not self.is_plotting:
            QMessageBox.critical(self,
            "Recording Cannot Start",
            "Please begin plotting before recording."
            )
        else:
            if len(record_deque) == 0:
                record_deque.append(1)
            self.rec_worker = RecordingWorker()
            self.rec_worker.start() 
            
            
                
    def stop(self):
        self.plot_timer.stop()
        self.is_plotting = False
        self.acq_worker.quit()
        time.sleep(1)
        if len(record_deque) > 0:
            _ = record_deque.popleft()
        if len(acq_deque) > 0:
            _ = acq_deque.popleft()
        time.sleep(3)
        self.acq_worker.quit()

    
class RecordingWorker(QtCore.QThread):
    def run(self):
        while len(record_deque) > 0:
            if len(img_deque) > 0:
                img_list = img_deque.popleft()
                if len(record_deque) > 0:
                    # Make sure this folder exists, otherwise it will result in an error
                    filename = 'images/img_%s.jpg' % (img_list[0])
                    # Crop Roi
                    np_img = img_list[1]
                    crop_img = np_img[roi_xmin:roi_xmax, roi_ymin:roi_ymax]
                    img = Image.fromarray(crop_img)
                    # Save image
                    img.save(filename)
                    # print('Image saved at %s\n' % filename)
            time.sleep(0.01)



class FLIRAcquisitionWorker(QtCore.QThread):
    def run(self):
        self.acq_main()
    
    def configure_trigger(self, cam):
        result = True

        print('*** CONFIGURING HARDWARE TRIGGER ***\n')
        try:
            # The trigger must be disabled in order to configure the source
            nodemap = cam.GetNodeMap()
            node_trigger_mode = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerMode'))
            if not PySpin.IsAvailable(node_trigger_mode) or not PySpin.IsReadable(node_trigger_mode):
                print('Unable to disable trigger mode (node retrieval). Aborting...')
                return False

            node_trigger_mode_off = node_trigger_mode.GetEntryByName('Off')
            if not PySpin.IsAvailable(node_trigger_mode_off) or not PySpin.IsReadable(node_trigger_mode_off):
                print('Unable to disable trigger mode (enum entry retrieval). Aborting...')
                return False

            node_trigger_mode.SetIntValue(node_trigger_mode_off.GetValue())

            print('Trigger mode disabled...')
            
            # Set TriggerSelector to FrameStart
            node_trigger_selector= PySpin.CEnumerationPtr(nodemap.GetNode('TriggerSelector'))
            if not PySpin.IsAvailable(node_trigger_selector) or not PySpin.IsWritable(node_trigger_selector):
                print('Unable to get trigger selector (node retrieval). Aborting...')
                return False

            node_trigger_selector_framestart = node_trigger_selector.GetEntryByName('FrameStart')
            if not PySpin.IsAvailable(node_trigger_selector_framestart) or not PySpin.IsReadable(
                    node_trigger_selector_framestart):
                print('Unable to set trigger selector (enum entry retrieval). Aborting...')
                return False
            node_trigger_selector.SetIntValue(node_trigger_selector_framestart.GetValue())
            
            print('Trigger selector set to frame start...')

            # Select trigger source
            node_trigger_source = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerSource'))
            if not PySpin.IsAvailable(node_trigger_source) or not PySpin.IsWritable(node_trigger_source):
                print('Unable to get trigger source (node retrieval). Aborting...')
                return False

            # Set trigger source to hardware
            node_trigger_source_hardware = node_trigger_source.GetEntryByName('Line0')
            if not PySpin.IsAvailable(node_trigger_source_hardware) or not PySpin.IsReadable(
                    node_trigger_source_hardware):
                print('Unable to set trigger source (enum entry retrieval). Aborting...')
                return False
            node_trigger_source.SetIntValue(node_trigger_source_hardware.GetValue())
            print('Trigger source set to hardware...')

            # Turn trigger mode on
            node_trigger_mode_on = node_trigger_mode.GetEntryByName('On')
            if not PySpin.IsAvailable(node_trigger_mode_on) or not PySpin.IsReadable(node_trigger_mode_on):
                print('Unable to enable trigger mode (enum entry retrieval). Aborting...')
                return False

            node_trigger_mode.SetIntValue(node_trigger_mode_on.GetValue())
            print('Trigger mode turned back on...')

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return False

        return result

    
    def configure_exposure(self, cam):
        print('*** CONFIGURING EXPOSURE ***\n')

        try:
            result = True

            # Turn off automatic exposure mode

            if cam.ExposureAuto.GetAccessMode() != PySpin.RW:
                print('Unable to disable automatic exposure. Aborting...')
                return False

            cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
            print('Automatic exposure disabled...')

            # Set exposure time manually; exposure time recorded in microseconds

            if cam.ExposureTime.GetAccessMode() != PySpin.RW:
                print('Unable to set exposure time. Aborting...')
                return False

            # Ensure desired exposure time does not exceed the maximum this is in us so 50 ms
            exposure_time_to_set = 30000.0
            exposure_time_to_set = min(cam.ExposureTime.GetMax(), exposure_time_to_set)
            cam.ExposureTime.SetValue(exposure_time_to_set)
            print('Shutter time set to %s us...\n' % exposure_time_to_set)

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False
        return result
    def acquire_images(self, cam, nodemap, nodemap_tldevice):

        print('*** IMAGE ACQUISITION ***\n')
        try:
            result = True

            # Set acquisition mode to continuous
            node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
            if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
                print('Unable to set acquisition mode to continuous (enum retrieval). Aborting...')
                return False

            # Retrieve entry node from enumeration node
            node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
            if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(
                    node_acquisition_mode_continuous):
                print('Unable to set acquisition mode to continuous (entry retrieval). Aborting...')
                return False

            # Retrieve integer value from entry node
            acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()

            # Set integer value from entry node as new value of enumeration node
            node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

            print('Acquisition mode set to continuous...')

            #  Begin acquiring images
            cam.BeginAcquisition()

            print('Acquiring images...')

            #  Retrieve device serial number for filename
            device_serial_number = ''
            node_device_serial_number = PySpin.CStringPtr(nodemap_tldevice.GetNode('DeviceSerialNumber'))
            if PySpin.IsAvailable(node_device_serial_number) and PySpin.IsReadable(node_device_serial_number):
                device_serial_number = node_device_serial_number.GetValue()
                print('Device serial number retrieved as %s...' % device_serial_number)

            # Retrieve, convert, and save images
            i = 0
            with nidaqmx.Task() as ctr_task:
                # Trigger for the camera, with an offset of 12.5 milliseconds from the LEDs
                #ctr_task.co_channels.add_co_pulse_chan_freq("Dev1/ctr0", freq=10, duty_cycle=0.5, initial_delay=0.025)
                # Trigger for BOTH LEDs, 470nm is directly connected, 405nm indirectly using a NOT gate
                #ctr_task.co_channels.add_co_pulse_chan_freq("Dev1/ctr1", freq=10, duty_cycle=0.5)
                # Run the task for an infinite amount of time until explicitly stopped
                # ctr_task.timing.cfg_implicit_timing(sample_mode=AcquisitionType.CONTINUOUS)
                # Start triggering
                #ctr_task.start()
                while len(acq_deque) > 0:
                    #  Retrieve next received image
                    image_result = cam.GetNextImage()

                    #  Ensure image completion
                    if image_result.IsIncomplete():
                        print('Image incomplete with image status %d ...' % image_result.GetImageStatus())

                    else:

                        # print('Grabbed Image %d' % (i))

                        #  Convert image to mono 8
                        img = image_result.Convert(PySpin.PixelFormat_Mono8, PySpin.HQ_LINEAR)

                        # Create a unique filename
                        t_file = datetime.datetime.now().strftime('%y-%m-%d_%H-%M-%S-%f')
                        t_plot = time.perf_counter()
                
                        """
                        # Make sure this folder exists, otherwise it will result in an error
                        filename = 'images/img_%s.jpg' % (t_file)
                        # Save image
                        img.Save(filename)
                        print('Image saved at %s\n' % filename)
                        """
                        
                        np_img = np.array(img.GetData(), dtype="uint8").reshape((img.GetHeight(), img.GetWidth()))

                        # Store timestamp and image in global queues for other functions to manipulate
                        img_deque.append([t_file, np_img])
                        img_plot_deque.append([t_plot, np_img])

                        #  Release image
                        image_result.Release()
                        # i += 1                
                # ctr_task.stop()
            cam.EndAcquisition()

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return False

        return result


    def reset_trigger(self, nodemap):
        try:
            result = True
            node_trigger_mode = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerMode'))
            if not PySpin.IsAvailable(node_trigger_mode) or not PySpin.IsReadable(node_trigger_mode):
                print('Unable to disable trigger mode (node retrieval). Aborting...')
                return False

            node_trigger_mode_off = node_trigger_mode.GetEntryByName('Off')
            if not PySpin.IsAvailable(node_trigger_mode_off) or not PySpin.IsReadable(node_trigger_mode_off):
                print('Unable to disable trigger mode (enum entry retrieval). Aborting...')
                return False

            node_trigger_mode.SetIntValue(node_trigger_mode_off.GetValue())

            print('Trigger mode disabled...')

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False

        return result
    
    def reset_exposure(self, cam):
        # Return the camera to a normal state by re-enabling automatic exposure.
        try:
            result = True
            if cam.ExposureAuto.GetAccessMode() != PySpin.RW:
                print('Unable to enable automatic exposure (node retrieval). Non-fatal error...')
                return False

            cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Continuous)

            print('Automatic exposure enabled...')

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False

        return result



    def run_single_camera(self, cam):
        try:
            result = True
            err = False

            # Retrieve TL device nodemap and print device information
            nodemap_tldevice = cam.GetTLDeviceNodeMap()

            # Initialize camera
            cam.Init()

            # Retrieve GenICam nodemap
            nodemap = cam.GetNodeMap()

            # Configure trigger
            if self.configure_trigger(cam) is False:
                return False

            # Configure exposure
            if self.configure_exposure(cam) is False:
                return False

            # Acquire images
            result &= self.acquire_images(cam, nodemap, nodemap_tldevice)

            # Reset trigger
            result &= self.reset_trigger(nodemap)

            # Reset exposure
            result &= self.reset_exposure(cam)
            
            # Deinitialize camera
            cam.DeInit()

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False

        return result


    def acq_main(self):
        result = True

        # Retrieve singleton reference to system object
        system = PySpin.System.GetInstance()

        # Retrieve list of cameras from the system
        cam_list = system.GetCameras()

        num_cameras = cam_list.GetSize()

        # Finish if there are no cameras
        if num_cameras == 0:
            # Clear camera list before releasing system
            cam_list.Clear()

            # Release system instance
            system.ReleaseInstance()

            print('Not enough cameras!')
            input('Done! Press Enter to exit...')
            return False

        # Run each camera
        for i, cam in enumerate(cam_list):

            print('Running camera %d...' % i)
            result &= self.run_single_camera(cam)
            print('Camera %d complete... \n' % i)

        # Release reference to camera
        del cam

        # Clear camera list before releasing system
        cam_list.Clear()

        # Release system instance
        system.ReleaseInstance()

        print('Done! Exiting program now.')
        return result


if __name__ == "__main__":
    app = QApplication(sys.argv)
    UIWindow = GUI()
    app.exec_()