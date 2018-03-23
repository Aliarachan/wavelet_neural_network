'''
Keras 1.2 + Theano.
'''
import os
os.environ['THEANO_FLAGS'] = "device=cuda0,floatX=float32,optimizer=fast_compile,optimizer_including=fusion, dnn.enabled=False"  
os.environ['CPLUS_INCLUDE_PATH'] = '/usr/local/cuda/include'

from keras.layers import Conv2D, Input, BatchNormalization, LeakyReLU, Dense, Flatten
from keras.models import Model
from keras.datasets import mnist
from keras.utils import np_utils

import WaveletLayer as wl

import math
import numpy as np

def build_haar_matrix(row_size):
    size = (int)(row_size / 2)
    haarM1 = np.zeros((size, row_size))
    for i in range(size):
        haarM1[i][2 * i] = math.sqrt(2) / 2
        haarM1[i][2 * i + 1] = math.sqrt(2) / 2

    haarM2 = np.zeros((size, row_size))
    for i in range(size):
        haarM2[i][2 * i] = math.sqrt(2) / 2
        haarM2[i][2 * i + 1] = -math.sqrt(2) / 2

    m = np.concatenate((haarM1, haarM2), axis=0)
    return m

haarMatrix28 = build_haar_matrix(28)
haarMatrix14 = build_haar_matrix(14)

(X_train, y_train), (X_test, y_test) = mnist.load_data()

x_train = X_train.reshape(X_train.shape[0], 1, 28, 28)
x_test = X_test.reshape(X_test.shape[0], 1, 28, 28)

x_train = x_train.astype('float32')
x_test = x_test.astype('float32')

number_of_classes = 10

y_train = np_utils.to_categorical(y_train, number_of_classes)
y_test = np_utils.to_categorical(y_test, number_of_classes)

print(y_train)

input = Input(shape=(1, 28, 28))
conv1 = Conv2D(20, 5,5, border_mode='same')(input)
batch1 = BatchNormalization()(conv1)

pool1 = wl.MyLayer(output_dim=(None, 20, 14, 14),  haar_matrix=haarMatrix28)(batch1)

conv2 = Conv2D(50,5,5,  border_mode='same')(pool1)

pool2 = wl.MyLayer(output_dim=(None, 50, 7, 7),  haar_matrix=haarMatrix14)(conv2)

batch2 = BatchNormalization()(pool2)

conv3 = Conv2D(500,4,4)(batch2)
relu = LeakyReLU(alpha=0)(conv3)
conv4 = Conv2D(10, 1, 1)(relu)
batch3 = BatchNormalization()(conv4)
flat = Flatten()(batch3)
activ = Dense(10, activation='softmax')(flat)
model = Model(input, activ)

model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])


model.fit(x_train, y_train, nb_epoch=5, batch_size=32)

loss_and_metrics = model.evaluate(x_test, y_test, batch_size=128)



print(loss_and_metrics)
