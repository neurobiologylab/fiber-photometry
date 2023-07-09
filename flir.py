   
import os
import datetime
import time
import numpy as np
import PySpin
import nidaqmx
from PIL import Image
from PySide2 import QtCore
from collections import deque
 
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

class RecordingWorker(QtCore.QThread):
    def __init__(self, deque_recording:deque, roi:ROI, images_folder_path:str, parent=None):
        self.deque_recording = deque_recording
        self.roi = roi
        self.images_folder_path = images_folder_path
        self.is_running = False
        super().__init__(parent)

    def run(self): 
        while self.is_running:
            if len(self.deque_recording) > 0:
                img_name, img = self.deque_recording.popleft()
                # Make sure this folder exists, otherwise it will result in an error
                filename = os.path.join(self.images_folder_path, f"img_{img_name}.jpg")
                # Crop Roi
                img = Image.fromarray(img[self.roi.xmin:self.roi.xmax, self.roi.ymin:self.roi.ymax])
                # Save image
                img.save(filename)
            time.sleep(0.01)





class FLIRAcquisitionWorker(QtCore.QThread):

    def __init__(self, deque_recording:deque, deque_plotting:deque, parent=None):
        self.deque_recording = deque_recording
        self.deque_plotting = deque_plotting
        self.is_running = False
        super().__init__(parent)

    def run(self):
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
            self.run_single_camera(cam)
            print('Camera %d complete... \n' % i)

        # Clear camera list before releasing system
        cam_list.Clear()

        # Release system instance
        system.ReleaseInstance()
        print('Done! Exiting program now.')
    
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
                while self.is_running:
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
                        
                        img = image_result.GetNDArray()
                        # np_img = np.array(img.GetData(), dtype="uint8").reshape((img.GetHeight(), img.GetWidth()))

                        # Store timestamp and image in global queues for other functions to manipulate
                        self.deque_recording.append([t_file, img])
                        self.deque_plotting.append([t_plot, img])

                        #  Release image
                        image_result.Release()
                        # i += 1                
                # ctr_task.stop()
            cam.EndAcquisition()

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)
            return False

        return result

