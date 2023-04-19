import cv2 
import os
import numpy as np
import matplotlib.pyplot as plt
import xlwt
import re
import csv

#============================================================================#
IMAGE_FOLDER = 'images'
PLOT_DATA = True
SAVE_TO_CSV = True
CSV_FILENAME = "experiment_data.csv"
SELECT_RANGE = False
MIN = 100
MAX = 200
#============================================================================#

images = [img for img in os.listdir(IMAGE_FOLDER) if img.endswith(".jpg")]
test_img = cv2.imread(os.path.join(IMAGE_FOLDER, images[0]))

# Select the indeces of the images for processing
# ind = len(images) // 2 - 3
# images = images[120:]

raw_intensity = []

for i in range(len(images) - 1):
    img_temp = cv2.imread(os.path.join(IMAGE_FOLDER, images[i]))
    img_sum = np.sum(img_temp)
    raw_intensity.append(img_sum)

if SELECT_RANGE == True:
    images = images[MIN:MAX]
    raw_intensity = raw_intensity[MIN:MAX]
    
x = range(len(images) - 1)

x405 = []
x470 = []
raw_intensity405 = []
raw_intensity470 = []
for i in range(len(x) - 1):
    if i % 2 == 0:
        x405.append(x[i])
        raw_intensity405.append(raw_intensity[i])
    else:
        x470.append(x[i])
        raw_intensity470.append(raw_intensity[i])

limit = len(x) // 2
x405 = x405[:(limit-1)]
x470 = x470[:(limit-1)]
raw_intensity405 = raw_intensity405[:(limit-1)]
raw_intensity470 = raw_intensity470[:(limit-1)]

sigma405 = np.std(raw_intensity405)
mu405 = np.average(raw_intensity405)
intensity405 = raw_intensity405 - mu405
intensity405 = intensity405 / sigma405
sigma470 = np.std(raw_intensity470)
mu470 = np.average(raw_intensity470)
intensity470 = raw_intensity470 - mu470
intensity470 = intensity470 / sigma470

raw_intensity470 = np.asarray(raw_intensity470)
raw_intensity405 = np.asarray(raw_intensity405)
raw_corrected470 = raw_intensity470 - raw_intensity405
corrected_sigma470 = np.std(raw_corrected470)
corrected_mu470 = np.average(raw_corrected470)
corrected470 = raw_corrected470 - corrected_mu470
corrected470 = corrected470 / corrected_sigma470

t405 = 0.1* np.asarray(x405)
t470 = 0.1* np.asarray(x470)

"""
if PLOT_DATA:
    plt.plot(t405, intensity405, color = 'purple', linewidth = 3)
    plt.xlabel("Time (s)")
    plt.ylabel("Light Intensity (Normalized)")
    plt.title("Fluorescence with 405nm LED")
    plt.show()

if PLOT_DATA:
    plt.plot(t470, intensity470, color = 'blue', linewidth = 3)
    plt.xlabel("Time (s)")
    plt.ylabel("Light Intensity (Normalized)")
    plt.title("Fluorescence with 470nm LED")
    plt.show()

if PLOT_DATA:
    plt.plot(t470, corrected470, color = 'green', linewidth = 3)
    plt.xlabel("Time (s)")
    plt.ylabel("Light Intensity (Normalized)")
    plt.title("Motion Corrected Fluorescence with 470nm LED")
    plt.show()
"""

if PLOT_DATA:
    #plt.style.use('extensys')
    ax1 = plt.subplot(121)
    ax1.plot(t405, intensity405, color = 'purple', linewidth = 3)
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Light Intensity (Normalized)")
    ax1.set_title("Fluorescence with 405nm LED")
    ax2 = plt.subplot(122)
    ax2.plot(t470, intensity470, color = 'blue', linewidth = 3)
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Light Intensity (Normalized)")
    ax2.set_title("Fluorescence with 470nm LED")
    plt.tight_layout
    plt.show()

import pandas as pd

data = {
    'Time (s)':t405,
    '405nm Normalized Light Intensity':intensity405, 
    'Time (s)':t470, 
    '470nm Normalized Light Intensity':intensity470,
    'Time (s)':t470,
    'Corrected Normalized 470 Light Intensity':corrected470
    }
DF1 = pd.DataFrame(data)
  
# save the dataframe as a csv file
if SAVE_TO_CSV: 
    DF1.to_csv(CSV_FILENAME)

"""
times = []
for file_name in images:
    t = 0
    year = int(file_name[4:6])
    month = int(file_name[7:9])
    day = int(file_name[10:12])
    hour = int(file_name[13:15])
    minute = int(file_name[16:18])
    second = int(file_name[19:21])
    micro = int(file_name[22:28])
    t += (year - 1) * (365.25*24*60*60)
    t += (month - 1) * ((365.25/12)*24*60*60)
    t += (day - 1) * (24*60*60)
    t += hour * 60 * 60
    t += minute * 60
    t += second 
    t += micro / 1000000
    times.append(t)
"""


"""
cv2.imshow('win', test_img)
cv2.waitKey(1000)
"""

"""
for image in images:
    cv2.imread(os.path.join(IMAGE_FOLDER, image))
"""
"""
Excel_Workbook = xlwt.Workbook()
sheet1 = Excel_Workbook.add_sheet("Test Data",cell_overwrite_ok=True)

"""