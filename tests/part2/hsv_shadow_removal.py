# -*- coding: utf-8 -*-
"""
Created on Sat May 20 10:05:26 2023
SHADOW REMOVAL HSV METHOD
@author: naray
"""

import numpy as np
import cv2
import matplotlib.pyplot as plt
image = cv2.imread('leaf1.png')
blank_mask = np.zeros(image.shape, dtype=np.uint8)
original = image.copy()
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# lower and upper are ranges for Hue, Saturation, and Value.
# Value (intensity) is fairly high.
lower = np.array([18, 42, 69])
upper = np.array([179, 255, 255])
mask = cv2.inRange(hsv, lower, upper)  
cv2.imshow("Mask (Different from the blank mask. This is just HSV result of cv2.inRange)", mask)
h, s, v = cv2.split(hsv)
cv2.imshow("Hue", h)
cv2.imshow("Saturation", s)
cv2.imshow("value", v)

cv2.imshow("In Range H", cv2.bitwise_and(h, mask))
cv2.imshow("In Range S", cv2.bitwise_and(s, mask))
cv2.imshow("In Range V", cv2.bitwise_and(v, mask))

# The above line shows the rough regions of the leaf (there are some missing holes in the image, but no shadow region is present).
# There is also some noise present in the image.    
cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

cnts = cnts[0] if len(cnts) == 2 else cnts[1]

# Reversing : White becomes black, and black becomes white because of reverse=True.
cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
for c in cnts:
    # For all contours, on the blank mask, draw a filled contour of color white.
    cv2.drawContours(blank_mask,[c], -1, (255,255,255), -1)
    break

result = cv2.bitwise_and(original,blank_mask)
cv2.imshow('original', original)
cv2.imshow('mask', blank_mask)
cv2.imshow('result', result)
cv2.waitKey()