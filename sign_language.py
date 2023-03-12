# import matplotlib.pyplot as plt
# import seaborn as sns
# from keras.models import Sequential
# from keras.layers import Dense, Conv2D, MaxPool2D, Flatten, Dropout, BatchNormalization
# from keras.preprocessing.image import ImageDataGenerator
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import classification_report, confusion_matrix
# import pandas as pd
# from sklearn.preprocessing import LabelBinarizer
#
#
# #import train and test files
# train_df = pd.read_csv("sign_mnist_train.csv")
# test_df = pd.read_csv("sign_mnist_test.csv")
#
# y = test_df['label']
#
# #plot show train label
# plt.figure(figsize = (7,7)) # Label Count
# sns.set_style("darkgrid")
# sns.countplot(train_df['label'])
#
#
# y_train = train_df['label']
# y_test = test_df['label']
#
#
# del train_df['label']
# del test_df['label']
#
# # train and test labels binarizer process (convert to array only includes [0,1] values)
# label_binarizer = LabelBinarizer()
# y_train = label_binarizer.fit_transform(y_train)
# y_test = label_binarizer.fit_transform(y_test)
#
# x_train = train_df.values
# x_test = test_df.values
#
# # we perform a grayscale normalization to reduce the effect of illumination's differences.
# # moreover the CNN converges faster on [0..1] data than on [0..255].
# x_train = x_train / 255
# x_test = x_test / 255
#
#
# # reshaping the data from 1-D to 3-D as required through input by CNN's
# x_train = x_train.reshape(-1, 28, 28, 1)
# x_test = x_test.reshape(-1, 28, 28, 1)
#
#
# # preview of first 10 images
# f, ax = plt.subplots(2,5)
# f.set_size_inches(10, 10)
# k = 0
# for i in range(2):
#     for j in range(5):
#         ax[i,j].imshow(x_train[k].reshape(28, 28) , cmap = "gray")
#         k += 1
#     plt.tight_layout()
#
# plt.show()
#
# # with data augmentation to prevent overfitting
# datagen = ImageDataGenerator(
#     featurewise_center=False,
#     samplewise_center=False,
#     featurewise_std_normalization=False,
#     samplewise_std_normalization=False,
#     zca_whitening=False,
#     rotation_range=10,
#     zoom_range=0.1,
#     width_shift_range=0.1,
#     height_shift_range=0.1,
#     horizontal_flip=False,
#     vertical_flip=False)
#
# datagen.fit(x_train)
#
# # creating a sequential model and show model summary
# model = Sequential()
# model.add(Conv2D(75, (3, 3), strides=1, padding='same', activation='relu', input_shape=(28, 28, 1)))
# model.add(BatchNormalization())
# model.add(MaxPool2D((2, 2), strides=2, padding='same'))
# model.add(Conv2D(50, (3, 3), strides=1, padding='same', activation='relu'))
# model.add(Dropout(0.2))
# model.add(BatchNormalization())
# model.add(MaxPool2D((2, 2), strides=2, padding='same'))
# model.add(Conv2D(25, (3, 3), strides=1, padding='same', activation='relu'))
# model.add(BatchNormalization())
# model.add(MaxPool2D((2, 2), strides=2, padding='same'))
# model.add(Flatten())
# model.add(Dense(units=512, activation='relu'))
# model.add(Dropout(0.3))
# model.add(Dense(units=24, activation='softmax'))
#
# model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
# model.summary()
#
# history = model.fit(datagen.flow(x_train, y_train, batch_size=128), epochs=20, validation_data=(x_test, y_test))
#
# # save model to avoid long training process
# model.save('smnist.h5')

import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
import cv2
import mediapipe as mp
from keras.models import load_model
import numpy as np
import time

# load model from pretrained model
model = load_model('smnist.h5')

mphands = mp.solutions.hands
hands = mphands.Hands()
mp_drawing = mp.solutions.drawing_utils

# open video capture from computer
cap = cv2.VideoCapture(0)
_, frame = cap.read()
# mapping frame shape to values
h, w, c = frame.shape

analysisframe = ''
letterpred = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
              'W', 'X', 'Y']

while True:
    _, frame = cap.read()

    k = cv2.waitKey(1)
    if k % 256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    elif k % 256 == 32:
        # SPACE pressed, analysis from capture and draw frame
        analysisframe = frame
        showframe = analysisframe
        cv2.imshow("Frame", showframe)
        framergbanalysis = cv2.cvtColor(analysisframe, cv2.COLOR_BGR2RGB)
        resultanalysis = hands.process(framergbanalysis)
        hand_landmarksanalysis = resultanalysis.multi_hand_landmarks
        if hand_landmarksanalysis:
            for handLMsanalysis in hand_landmarksanalysis:
                x_max = 0
                y_max = 0
                x_min = w
                y_min = h
                for lmanalysis in handLMsanalysis.landmark:
                    x, y = int(lmanalysis.x * w), int(lmanalysis.y * h)
                    if x > x_max:
                        x_max = x
                    if x < x_min:
                        x_min = x
                    if y > y_max:
                        y_max = y
                    if y < y_min:
                        y_min = y
                y_min -= 20
                y_max += 20
                x_min -= 20
                x_max += 20

        analysisframe = cv2.cvtColor(analysisframe, cv2.COLOR_BGR2GRAY)
        analysisframe = analysisframe[y_min:y_max, x_min:x_max]
        analysisframe = cv2.resize(analysisframe, (28, 28))

        nlist = []
        rows, cols = analysisframe.shape
        for i in range(rows):
            for j in range(cols):
                k = analysisframe[i, j]
                nlist.append(k)

        datan = pd.DataFrame(nlist).T
        colname = []
        for val in range(784):
            colname.append(val)
        datan.columns = colname

        pixeldata = datan.values
        pixeldata = pixeldata / 255
        pixeldata = pixeldata.reshape(-1, 28, 28, 1)

# prediction process
# print top 3 high confidence predicted letters on screen
prediction = model.predict(pixeldata)
predarray = np.array(prediction[0])
letter_prediction_dict = {letterpred[i]: predarray[i] for i in range(len(letterpred))}
predarrayordered = sorted(predarray, reverse=True)
high1 = predarrayordered[0]
high2 = predarrayordered[1]
high3 = predarrayordered[2]
for key, value in letter_prediction_dict.items():
    if value == high1:
        print("Predicted Character 1: ", key)
        print('Confidence 1: ', 100 * value)
    elif value == high2:
        print("Predicted Character 2: ", key)
        print('Confidence 2: ', 100 * value)
    elif value == high3:
        print("Predicted Character 3: ", key)
        print('Confidence 3: ', 100 * value)
time.sleep(5)
