# -*- coding: utf-8 -*-
"""KneeMRI_worked.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15mXAzDzobDCofMyapciArfIM2b3frCxo
"""

from google.colab import files
src = list(files.upload().values())[0]
open('vb100_utils.py','wb').write(src)
import vb100_utils

!pip uninstall keras-nightly
!pip uninstall -y tensorflow

#! pip install tensorflow==2.1.0
!pip install tensorflow==1.13.1
! pip install keras==2.2.4

# Commented out IPython magic to ensure Python compatibility.
# Import modules and packages
import numpy as np
import pandas as pd
import itertools
import os, stat, time
from os.path import dirname as up

import tensorflow as tf
import keras
from keras import backend as K
from keras.models import Sequential
from keras.layers import Activation
from keras.layers.core import Dense, Flatten, Dropout
from keras.optimizers import Adam
from keras.optimizers import RMSprop
from keras.metrics import categorical_crossentropy
from keras.regularizers import l2
from keras.preprocessing.image import ImageDataGenerator
from keras.layers.convolutional import *
from keras.layers.normalization import BatchNormalization
from keras.optimizers import SGD

from matplotlib import pyplot as plt

from sklearn.metrics import confusion_matrix
from vb100_utils import *

#from vb100_utils import *
from shutil import copyfile
import shutil
import glob
from PIL import Image

import warnings
warnings.filterwarnings('ignore')
# %matplotlib inline
from google.colab import drive

!pip install sklearn
!pip install -U matplotlib
!pip install Pillow

drive.mount('/content/drive')

data_dir = '/content/drive/MyDrive/Data/'
!ls -lh $data_dir

print('Tensorflow version = {}'.format(tf.__version__))
print('Keras version = {}'.format(keras.__version__))

# CONSTANTS FOR DIRECTORIES
TRAIN_DIR = '/content/drive/MyDrive/Data/train'
VALID_DIR = '/content/drive/MyDrive/Data/valid'
#TEST_DIR = '/content/drive/MyDrive/Data/test'
#TEST_DIR = '/content/drive/MyDrive/Data/train'
l_DIRS = [TRAIN_DIR, VALID_DIR]
POSITIVE_CLASS = 'ABNORMAL'
ABSTRACT_CLASS = 'ACL'

# CONSTANTS FOR IMAGE PARAMETERS
INPUT_W = 1200 # pixels
INPUT_H = 900  # pixels
DIVIDER = 3.6
INPUT_DIM = (int(INPUT_W/DIVIDER), int(INPUT_H/DIVIDER), 1)
BATCH_SIZE_TRAIN = 64
BATCH_SIZE_TEST = 64 
BATCH_SIZE_VALID = 16
NORMALIZER = 1./255
#IMAGE_FORMAT = '.npy'
IMAGE_FORMAT = 'jpg'

# Output Info
print('Image dimmensions for CNN = {}'.format(INPUT_DIM))

if abstract_class_exists(ABSTRACT_CLASS, l_DIRS):
   structure_origin_data(l_DIRS, IMAGE_FORMAT, POSITIVE_CLASS)

classes = classes_for_each_set(l_DIRS)

print('Catched classes for the model:\n{}'.format(classes))

# Generating and Plot Image Data from Train Set
TRAIN_BATCHES = ImageDataGenerator(rescale=NORMALIZER).\
    flow_from_directory(TRAIN_DIR,
    color_mode='grayscale',
    target_size=INPUT_DIM[0:2],
    classes=classes['TRAIN'],
    class_mode="categorical",
    shuffle=True,
    batch_size=BATCH_SIZE_TRAIN)

imgs, labels = next(TRAIN_BATCHES)  # <-- Extracting image matrixes and labels
plots(imgs, titles=labels)          # <-- Plot Images with labels
#train_imgs = rgb_to_grayscale(imgs) # <-- Convert RGB images to Grayscale ones by Tensorflow
#train_labels = labels

# Generating and Plot Image Data from Validation Set
VAL_BATCHES = ImageDataGenerator(rescale=NORMALIZER).\
    flow_from_directory(VALID_DIR,
    color_mode='grayscale',
    target_size=INPUT_DIM[0:2],
    classes=classes['VALIDATION'],
    class_mode="categorical",
    shuffle=True,
    batch_size=BATCH_SIZE_VALID)

imgs, labels = next(VAL_BATCHES)   # <-- Extracting image matrixes and labels
plots(imgs, titles=labels)         # <-- Plot Images with labels
#val_imgs = rgb_to_grayscale(imgs)  # < -- Convert RGB images to Grayscale ones by Tensorflow
#val_labels = labels

# Output of Generators
for data_batch, label_batch in TRAIN_BATCHES:
    print('data batch shape = {}'.format(data_batch.shape))
    print('labels batch shape = {}'.format(label_batch.shape))
    break



# Build the CNN model
#tf.compat.v1.reset_default_graph()

#import tensorflow.compat.v1 as tf
#tf.disable_v2_behavior()
#from tensorflow.keras import backend as k
#from tensorflow.python.keras import backend as k
#from tensorflow.python.framework import ops
#ops.get_default_graph()


model = Sequential()
model.add(Conv2D(64, (5, 5), input_shape=(INPUT_DIM)))
model.add(Activation('relu'))
model.add(MaxPooling2D((3, 3)))

model.add(Conv2D(128, (4, 4))) 
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Conv2D(512, (3, 3))) 
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Conv2D(512, (3, 3))) 
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Conv2D(512, (3, 3))) 
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Conv2D(512, (2, 2))) 
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Flatten()) 

model.add(Dense(512, kernel_regularizer=regularizers.l2(0.02))) 
model.add(Activation('relu'))

model.add(Dense(3)) 
model.add(Activation('softmax'))

model.summary()

# Define an optimizer for the model
import tensorflow as tf
tf.compat.v1.disable_eager_execution()

opt = Adam(lr=0.00001, beta_1=0.9, beta_2=0.999,epsilon=None, decay=0.0, amsgrad=False)
#opt = SGD(lr=0.01, decay=1e-6, momentum=0.85, nesterov=True)
#opt = RMSprop(lr=0.001, rho=0.8, epsilon=None, decay=0.0)

model.compile(loss='categorical_crossentropy', metrics=['accuracy'],
optimizer=opt)

print('steps_per_epoch={}'.format(int(182 / BATCH_SIZE_TRAIN)))
print('validation_steps={}'.format(int(170 / BATCH_SIZE_TEST)))

#print('steps_per_epoch={}'.format(int(4 / 2)))
#print('validation_steps={}'.format(int(6 / 6)))

# Commented out IPython magic to ensure Python compatibility.
# %%time
# model.fit_generator(
#     TRAIN_BATCHES,
#     steps_per_epoch=len(TRAIN_BATCHES),
#     validation_data=VAL_BATCHES,
#     validation_steps=len(VAL_BATCHES),
#     epochs=2,
#     verbose=2
# )
# 
# # Parameters meanings:
# # steps_per_epoch = number_of_images / batch_size = 5215 / 64 = 82:
# # --- Total number of steps (batches of samples) to yield from generator before declaring one 
# #     epoch finished and starting the next epoch. It should typically be equal to the number 
# #     of unique samples of your dataset divided by the batch size.
# # Verbose:
# # -- 0 (quiet): you just get the total numbers of tests executed and the global result
# # -- 1 (default): you get the same plus a dot for every successful test or a F for every failure
# # -- 2 (verbose): you get the help string of every test and the result

from google.colab import files
src = list(files.upload().values())[0]
open('vb100_utils.py','wb').write(src)
import vb100_utils

plot_model_result(model)

# Save the results as separate lists
df = save_model_result(model)

# Save the Model Weights
model.save_weights('/content/drive/MyDrive/model_keras.h5')

# Save the Model to JSON
model_json = model.to_json()
with open('/content/drive/MyDrive/model1.json', 'w') as json_file:
    json_file.write(model_json)
    
print('Model saved to the disk.')

# ------------------------------------------------------------------------
# Load saved model and its weights
'''
>> Model weights are saved to HDF5 format.
>> The model structure can be described and saved using two different formats: JSON and YAML.
'''

# Import dependencies
from keras.optimizers import Adam
from tensorflow.keras.models import model_from_json
from tensorflow.python.framework import ops
ops.reset_default_graph()
import h5py 
from PIL import Image
import PIL
from vb100_utils import *

print('h5py version is {}'.format(h5py.__version__))

# Get the architecture of CNN
json_file = open('/content/drive/MyDrive/model1.json')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)

# Get weights into the model
loaded_model.load_weights('/content/drive/MyDrive/model_100_eopchs_adam_20191030_01.h5')

classes = {'TRAIN': ['axial', 'coronal', 'sagittal'],
           'VALIDATION': ['axial', 'coronal', 'sagittal']}
IMG = Image.open('/content/drive/MyDrive/coronal2.jpg')
print(type(IMG))
print(IMG.size)
IMG = IMG.resize((333, 250))
#IMG = IMG.resize((342, 257))
IMG = np.array(IMG)
print('po array = {}'.format(IMG.shape))
IMG = np.true_divide(IMG, 255)
IMG = IMG.reshape(64, 333, 250, 1)
#IMG = IMG.reshape(-1, 1, 342, 257)
#data.reshape((-1, 1, 28, 28))

#IMG = IMG.reshape(1, 200, 255, 1)
print(type(IMG), IMG.shape)

predictions = loaded_model.predict(IMG)

print(loaded_model)
predictions_c = loaded_model.predict_classes(IMG)
print(predictions, predictions_c)
predicted_class = classes['TRAIN'][predictions_c[0]]
print('We think that is {}.'.format(predicted_class.lower()))

'''
Here I will simulate what will happen during deployment on a cloud.
Reading a given image, preparing it for CNN evaluation and make
a predictions with a returned class from a dictionary that has
been used for training.
'''

# Define optimizer and run
opt = Adam(lr=0.00001, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0)
model.compile(loss='categorical_crossentropy', metrics=['accuracy'], optimizer='rmsprop')


'''
Important Note! For this block optimizer is entered manualy as Tensorflow object.
For future, need to change it for include it as variable with full set of
parameters as Tensorflow variable.

'''
#TRAIN_DIR = '/content/drive/MyDrive/Data/train'
#VALID_DIR = '/content/drive/MyDrive/Data/valid'
IMG = Image.open('/content/drive/MyDrive/coronal2.jpg')
print(type(IMG))
print(IMG.size)
IMG = IMG.resize((342, 257))
IMG = np.array(IMG)
print('po array = {}'.format(IMG.shape))
IMG = np.true_divide(IMG, 255)
IMG = IMG.reshape(64, 333, 250, 1)
#IMG = IMG.reshape(1, 200, 255, 1)
print(type(IMG), IMG.shape)

predictions = loaded_model.predict(IMG)

print(loaded_model)
predictions_c = loaded_model.predict_classes(IMG)
print(predictions, predictions_c)