#!/usr/bin/env python
# coding: utf-8

# In[1]:


import cv2 
import os
import numpy as np
import matplotlib.pyplot as plt
import xlwt
import re
import csv
import os # operation system
from sklearn.linear_model import LinearRegression 
os.makedirs("exp20221014")

#============================================================================#
IMAGE_FOLDER = 'Images'
#============================================================================#
PLOT_DATA = True
#============================================================================#
SAVE_TO_CSV = True
CSV_FILENAME = "exp20221014/experiment_data.csv"
#============================================================================#
SELECT_RANGE = False
MIN = 100
MAX = 200
#============================================================================#


# In[2]:


images = [img for img in os.listdir(IMAGE_FOLDER) if img.endswith(".jpg")]
# print(images)
print(len(images))
# images = []
# for img in os.listdir(IMAGE_FOLDER):
#     if img.endswith(".jpg"):
#         images.append(img)


# In[3]:


images = images[:-1] # just so we have an even number of images
print(len(images))


# In[4]:


test_img = cv2.imread(os.path.join(IMAGE_FOLDER, images[0]))

# Select the indeces of the images for processing
# ind = len(images) // 2 - 3
# images = images[120:]


# In[5]:


test_img.shape


# In[6]:


test_img[:, :, :1].shape


# In[7]:


test_img[:, :, 0].shape


# In[8]:


np.min(test_img[:, :, 0])


# In[9]:


np.max(test_img[:, :, 0] - test_img[:, :, 2])


# In[10]:


np.min(test_img[:, :, 0] - test_img[:, :, 2])


# In[11]:


test_img[:, :, 0]


# In[12]:


raw_intensity = []

# this is a loop with len(images)-1 iterations, i.e. i has len(images)-1 possible values
# i starts with 0, ends with len(image)-2, len(image)-1 is excluded
# in python, we count from 0; left inclusive, right exclusive
for i in range(len(images)): 
    img_temp = cv2.imread(os.path.join(IMAGE_FOLDER, images[i]))
    img_sum = np.mean(img_temp)
    raw_intensity.append(img_sum)

if SELECT_RANGE: # opposite: if not SELECT_RANGE
    images = images[MIN:MAX]
    raw_intensity = raw_intensity[MIN:MAX]


# In[13]:


len(raw_intensity)


# In[14]:


# x has len(images) elements
# starts with 0, ends with len(images)-1, len(images) is excluded
x = range(len(images))

x405 = [i for i in range(0, len(images), 2)]
x470 = [i for i in range(1, len(images), 2)]
raw_intensity405 = []
raw_intensity470 = []
for i in range(len(images)):
    if i % 3 == 0:
        raw_intensity405.append(raw_intensity[i])
    elif i % 3 == 1:
        raw_intensity470.append(raw_intensity[i])

# turn lists into arrays for numerical computation
raw_intensity470 = np.asarray(raw_intensity470)
raw_intensity405 = np.asarray(raw_intensity405)

# time
t405 = 0.1* np.asarray(x405)
t470 = 0.1* np.asarray(x470)


# In[15]:


##### Step 4 #####
sigma405 = np.std(raw_intensity405)
mu405 = np.mean(raw_intensity405)
intensity405 = raw_intensity405 - mu405
intensity405 = intensity405 / sigma405

sigma470 = np.std(raw_intensity470)
mu470 = np.mean(raw_intensity470)
intensity470 = raw_intensity470 - mu470
intensity470 = intensity470 / sigma470


# In[16]:


from sklearn.linear_model import LinearRegression

linr_model = LinearRegression().fit(intensity405.reshape(-1, 1), intensity470)


# In[17]:


print(linr_model.coef_)
print(linr_model.intercept_)


# In[18]:


fit405 = linr_model.coef_[0] * intensity405 + linr_model.intercept_


# In[19]:


dF_F = intensity470 - fit405


# In[20]:


if PLOT_DATA:
    fig, ax = plt.subplots(2, 1, figsize=(15,10))
    
    ax[0].plot(t405, raw_intensity405, color = 'purple', linewidth = 0.5)
    ax[0].set_xlabel("Time (s)")
    ax[0].set_ylabel("Light Intensity (Raw)")
    ax[0].set_title("Fluorescence with 405nm LED")
    ax[1].plot(t470, raw_intensity470, color = 'blue', linewidth = 0.5)
    ax[1].set_xlabel("Time (s)")
    ax[1].set_ylabel("Light Intensity (Raw)")
    ax[1].set_title("Fluorescence with 470nm LED")
    plt.show()


# In[21]:


if PLOT_DATA:
    fig, ax = plt.subplots(3, 1, figsize=(15,15))

    ax[0].plot(t405, intensity405, color = 'purple', linewidth = 0.5)
    ax[0].set_xlabel("Time (s)")
    ax[0].set_ylabel("Light Intensity (Normalized)")
    ax[0].set_title("Fluorescence with 405nm LED")
    ax[1].plot(t470, intensity470, color = 'blue', linewidth = 0.5)
    ax[1].set_xlabel("Time (s)")
    ax[1].set_ylabel("Light Intensity (Normalized)")
    ax[1].set_title("Fluorescence with 470nm LED")
    ax[2].plot(t470, dF_F, color = 'green', linewidth = 0.5)
    ax[2].set_xlabel("Time (s)")
    ax[2].set_ylabel("Light Intensity (Normalized)")
    ax[2].set_title("Fluorescence with corrected 470nm LED")
    plt.show()


# In[24]:


import pandas as pd

data = {
    '405nm Time (s)': t405,
    '405nm Raw Light Intensity': raw_intensity405, 
    '405nm Normalized Light Intensity': intensity405, 
    '470nm Time (s)': t470, 
    '470nm Raw Light Intensity': raw_intensity470,
    '470nm Normalized Light Intensity': intensity470,
    'Corrected 470nm Time (s)': t470,
    'Corrected Normalized 470 Light Intensity': dF_F
}
DF1 = pd.DataFrame(data)
  
# save the dataframe as a csv file
if SAVE_TO_CSV: 
    DF1.to_csv(CSV_FILENAME)


# In[23]:





# In[ ]:




