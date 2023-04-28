import matplotlib.pyplot as plt
import cv2
import numpy as np
from pathlib import Path
import os

frames = []
differences = []

vid = cv2.VideoCapture('../data/showcase/PointCloudVisualizer.mp4')

# checks whether frames were extracted
success = 1

while success:

    success, image = vid.read()
    frames.append(image)


for i in range(len(frames)-2):
    differences.append(np.sum(np.abs(frames[i+1] - frames[i])))

differences = np.array(differences)

max_frame_index = differences.argmax(axis=0)
print("Max difference of sum of abs between two consecutive frames", differences[max_frame_index])
print('Frame indices : ', max_frame_index, ' and ', max_frame_index+1)
plt.imshow(frames[max_frame_index])
plt.show()
plt.imshow(frames[max_frame_index+1])