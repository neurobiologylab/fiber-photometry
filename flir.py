import os
import datetime
import numpy as np
import PySpin
from PIL import Image
from PySide2.QtCore import QObject, Signal, Slot
 
class ROI():
    def __init__(self, roi):
        """
        Initialize the ROI object.
        
        Parameters:
            roi (list): A list of 4 items representing [Top_Left_X, Top_Left_Y, Width, Height] of the ROI.
        """
        self.xmin = roi[1]
        self.xmax = roi[1] + roi[3]
        self.ymin = roi[0]
        self.ymax = roi[0] + roi[2]

class Worker(QObject):
    frequency = Signal(float)
    elapsed_time = Signal(int)
    completed = Signal(bool)
    def __init__(self, roi:ROI, images_folder_path:str, images_save:bool=False, exposure_time = 30000.0, parent=None):
        self.image_acquisition = [{"images": [], "mean":[], "time": []},{"images": [], "mean":[], "time": []}, {"images": [], "mean":[], "time": []}]
        self.roi = roi
        self.images_folder_path = images_folder_path
        self.image_save = images_save
        self.running = False
        self.exposure_time = exposure_time
        self.t0 = 0
        super().__init__(parent)    
        
    @Slot(bool)
    def set_running(self, running):
        self.running = running
        if not self.running:
            self.flir.reset_trigger()
    @Slot()
    def do_work(self):
        i = 0
        self.flir = FLIR()
        status = (self.flir.init_acquisition(exposure_time=self.exposure_time)) and (self.flir.cam is not None)
        while self.running & status:
            img = self.flir.acquire_image()[self.roi.xmin:self.roi.xmax, self.roi.ymin:self.roi.ymax]
            if i == 0:
                self.t0 = datetime.datetime.now()
            channel = i%3       
            seconds_elapsed = (datetime.datetime.now()-self.t0).total_seconds()
            self.image_acquisition[channel]["images"].append(img)
            self.image_acquisition[channel]["mean"].append(np.mean(img))
            self.image_acquisition[channel]["time"].append(seconds_elapsed)  
            if self.image_save:        
                folder_path = os.path.join(self.images_folder_path, f"chn{channel}")
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)      
                filename = os.path.join(folder_path, f"{datetime.datetime.now().strftime('%y-%m-%d_%H-%M-%S-%f')}.jpg")
                imag = Image.fromarray(img)
                Image.fromarray(img).save(filename)  
            if  seconds_elapsed > 0:
                self.elapsed_time.emit(seconds_elapsed)             
                self.frequency.emit(float(i)/seconds_elapsed)             
            i+=1

        self.flir.end_acquisition()
        self.flir.release()
        self.completed.emit(True)


class FLIR():
    def __init__(self):
        # Retrieve singleton reference to system object
        self.system = PySpin.System.GetInstance()
        # Retrieve list of cameras from the system
        self.cam_list = self.system.GetCameras()
        num_cameras = self.cam_list.GetSize()
        # Finish if there are no cameras
        if num_cameras == 0:
            print('No Camera Found!')
            self.cam = None
            self.release()
        else:
            self.cam = self.cam_list[0]

    def release(self):
        del self.cam
        # Clear camera list before releasing system
        self.cam_list.Clear()
        # Release system instance
        self.system.ReleaseInstance()

    def take_single_pic(self, exposure_time=30000.0):
        if self.cam is None:
            return False, None
        result = True
        img = None
        try:
            # Retrieve TL device nodemap and print device information
            self.nodemap_tldevice = self.cam.GetTLDeviceNodeMap()

            # Initialize camera
            self.cam.Init()

            # Retrieve GenICam nodemap
            self.nodemap = self.cam.GetNodeMap()
            # Configure exposure
            if not self.configure_exposure(exposure_time):
                return False, img
            result &= self.reset_trigger()
            # Acquire images
            result &= self.acquire_init()
            img = self.acquire_image()
            result &= self.acquire_end()

            # Reset exposure
            result &= self.reset_exposure()
            
            # Deinitialize camera
            self.cam.DeInit()
            self.release()

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False
        finally:
            return result, img

    def init_acquisition(self, exposure_time=30000.0):
        result = True
        try:
            # Retrieve TL device nodemap and print device information
            self.nodemap_tldevice = self.cam.GetTLDeviceNodeMap()

            # Initialize camera
            self.cam.Init()

            # Retrieve GenICam nodemap
            self.nodemap = self.cam.GetNodeMap()

            # Configure trigger
            if not self.configure_trigger():
                return False
            
            # Configure exposure
            if not self.configure_exposure(exposure_time):
                return False
            result &= self.acquire_init()

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False
        finally:
            return result

    def end_acquisition(self):
        result = True
        try:
            result &= self.acquire_end()

            # Reset trigger
            result &= self.reset_trigger()

            # Reset exposure
            result &= self.reset_exposure()
                
            # Deinitialize camera
            self.cam.DeInit()

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False
        finally:
            return result




    def configure_exposure(self, exposure_time = 30000.0): 
        print('*** CONFIGURING EXPOSURE ***\n')

        try:
            result = True

            # Turn off automatic exposure mode
            if self.cam.ExposureAuto.GetAccessMode() != PySpin.RW:
                print('Unable to disable automatic exposure. Aborting...')
                return False
            self.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
            print('Automatic exposure disabled...')
            # Set exposure time manually; exposure time recorded in microseconds
            if self.cam.ExposureTime.GetAccessMode() != PySpin.RW:
                print('Unable to set exposure time. Aborting...')
                return False
            # Ensure desired exposure time does not exceed the maximum this is in us so 50 ms
            exposure_time_to_set = min(self.cam.ExposureTime.GetMax(), exposure_time)
            self.cam.ExposureTime.SetValue(exposure_time_to_set)
            print('Shutter time set to %s us...\n' % exposure_time_to_set)

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False
        return result
          
    def reset_exposure(self):
        # Return the camera to a normal state by re-enabling automatic exposure.
        try:
            result = True
            if self.cam.ExposureAuto.GetAccessMode() != PySpin.RW:
                print('Unable to enable automatic exposure (node retrieval). Non-fatal error...')
                return False

            self.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Continuous)

            print('Automatic exposure enabled...')

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False

        return result
    
    def configure_trigger(self):
        result = True
        print('*** CONFIGURING HARDWARE TRIGGER ***\n')
        try:
            # The trigger must be disabled in order to configure the source
            node_trigger_mode = PySpin.CEnumerationPtr(self.nodemap.GetNode('TriggerMode'))
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
            node_trigger_selector= PySpin.CEnumerationPtr(self.nodemap.GetNode('TriggerSelector'))
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
            node_trigger_source = PySpin.CEnumerationPtr(self.nodemap.GetNode('TriggerSource'))
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
    
    def reset_trigger(self):
        try:
            result = True
            node_trigger_mode = PySpin.CEnumerationPtr(self.nodemap.GetNode('TriggerMode'))
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
        
    def acquire_init(self):
        print('*** IMAGE ACQUISITION ***\n')
        try:
            result = True
            # Set acquisition mode to continuous
            node_acquisition_mode = PySpin.CEnumerationPtr(self.nodemap.GetNode('AcquisitionMode'))
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
            self.cam.BeginAcquisition()
            print('Acquiring images...')
            #  Retrieve device serial number for filename
            node_device_serial_number = PySpin.CStringPtr(self.nodemap_tldevice.GetNode('DeviceSerialNumber'))
            if PySpin.IsAvailable(node_device_serial_number) and PySpin.IsReadable(node_device_serial_number):
                device_serial_number = node_device_serial_number.GetValue()
                print('Device serial number retrieved as %s...' % device_serial_number)
            return True

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return False

        return result

    def acquire_image(self):
        try:
            #  Retrieve next received image
            image_result = self.cam.GetNextImage()

            #  Ensure image completion
            if image_result.IsIncomplete():
                print('Image incomplete with image status %d ...' % image_result.GetImageStatus())
                return None
            else:
                #  Convert image to mono 8
                img = image_result.Convert(PySpin.PixelFormat_Mono8, PySpin.HQ_LINEAR)

                img = image_result.GetNDArray()
                #  Release image
                image_result.Release()
                return img

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return None
            
    def acquire_end(self):
        try:
            self.cam.EndAcquisition()

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return False
        return True
    


    




