
from PySide2 import QtGui
from PySide2.QtWidgets import (
    QLabel,
    QMainWindow,
    QApplication,
    QPushButton,
    QDialogButtonBox,
    QSlider,QWidget,QMessageBox,QLCDNumber
)
from PySide2.QtGui import QPixmap
from experiment_setup_ui import SettingsUI
import numpy as np
import cv2
import PySpin
import sys
import os
import copy
import qimage2ndarray
import pyqtgraph as pg
from flir import ROI

# uiclass, baseclass = pg.Qt.loadUiType("parameter_window.ui")
# uiclass, baseclass = pg.Qt.loadUiType("parameter_window_temp.ui")


class Settings(QMainWindow):
    def __init__(self, parent=None):
        super(Settings, self).__init__(parent=parent)
        ui = SettingsUI()
        ui.setupUi(self)
        # Customize title and icon in window corner
        self.setWindowTitle("New Experiment Setup")
        # self.setWindowIcon(QtGui.QIcon('nbi-logo.jpg'))

        self.btn_update_img = self.findChild(QPushButton, "updateImageButton")
        self.btn_roi = self.findChild(QPushButton, "btn_roi")
        self.lcd_test = self.findChild(QLCDNumber, "lcd_test")
        # self.wid = self.findChild(QWidget, "wid_panel")
        # self.wid.hide()
        # self.btn_roi.hide()
        self.img_display = self.findChild(QLabel, "lbl_display")
        self.dbb_ok_cancel = self.findChild(QDialogButtonBox, "dbb_ok_cancel")
        # # self.dbb_ok_cancel.hide()
        # self.btn_update_img.hide()

        self.btn_update_img.clicked.connect(self.update_img)
        self.btn_roi.clicked.connect(self.select_roi)
        self.dbb_ok_cancel.accepted.connect(self.param_selected)
        self.dbb_ok_cancel.rejected.connect(self.param_selected)

        self.roi_xmin = 0
        self.roi_ymin = 0
        self.roi_xmax = 500
        self.roi_ymax = 500

        self.is_ROI_selected = False
        self.is_param_selected = False

        self.image = np.zeros(1)

        self.show()

    def update_img(self):
        self.get_img()

        if self.is_ROI_selected == True:
            img = copy.copy(self.image)
            img_crop = img[
                self.roi_xmin : self.roi_xmax, self.roi_ymin : self.roi_ymax
            ]
            # Opencv uses bgr colors, we convert since QImage uses rgb
            img_rgb = cv2.cvtColor(img_crop, cv2.COLOR_BGR2RGB)
            # Opencv creates a numpy array, but QPixmap requires a QImage
            qImg = qimage2ndarray.array2qimage(img_rgb)
            # Display the image in the label widget of the GUI
            self.img_display.setPixmap(QPixmap(qImg))
        else:
            img = copy.copy(self.image)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            qImg = qimage2ndarray.array2qimage(img_rgb)
            self.img_display.setPixmap(QPixmap(qImg))


    def select_roi(self):
        self.get_img()
        try:
            img = cv2.cvtColor(self.image, cv2.COLOR_BAYER_BG2RGB)
            # img = copy.copy(self.image)
            roi = cv2.selectROI(img)
            self.roi = ROI(roi)
            # self.roi_xmin, self.roi_xmax = int(roi[1]), int(roi[1] + roi[3])
            # self.roi_ymin, self.roi_ymax = int(roi[0]), int(roi[0] + roi[2])
            # Crop the image using the user selected roi
            img_crop = img[self.roi.xmin:self.roi.xmax, self.roi.ymin:self.roi.ymax]
            # If the user has selected a roi, close the original window
            if self.roi_xmax > 0 or self.roi_ymax > 0:
                cv2.destroyAllWindows()
            # Wait infinitely until the user presses a key
            cv2.waitKey(0)
            # Show the cropped image in a new window
            cv2.imshow("Image", img_crop)
            self.is_ROI_selected = True
            QMessageBox.critical(self,"Error", f"{self.roi.xmin},{self.roi.xmax}, {self.roi.ymin},{self.roi.ymax}")
            self.lcd_test.setText(f"{self.roi.xmin},{self.roi.xmax}, {self.roi.ymin},{self.roi.ymax}")
        except:
            cv2.destroyAllWindows()
            self.is_ROI_selected = False

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
                image_result = cam.GetNextImage(1000)

                if image_result.IsIncomplete():
                    print('Image incomplete with image status %d ...' % image_result.GetImageStatus())

                else:
                    img = image_result.Convert(PySpin.PixelFormat_Mono8, PySpin.HQ_LINEAR)
                    self.image = np.array(img.GetData(), dtype="uint8").reshape((img.GetHeight(), img.GetWidth()))
                    image_result.Release()
                    # image_data = image_result.GetNDArray()


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


    def param_selected(self):
        self.is_param_selected = True
        self.close()

    def no_param_selected(self):
        self.is_param_selected = False
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    UIWindow = Settings()
    app.exec_()

