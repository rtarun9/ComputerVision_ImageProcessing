import cv2
import numpy as np

# Create canvas (300x300) having 3 color channels.
canvas = np.zeros((300, 300, 3))

# Drawing a lien on canvas.
cv2.line(canvas, (0, 0), (300, 300), (255, 0, 0), 3, cv2.LINE_AA)
cv2.line(canvas, (299, 0), (0, 288), (0, 255, 0), 3, cv2.LINE_AA)

# Drawing a rectangle.
cv2.rectangle(canvas, (100, 100), (200, 200), (255, 255, 0), -1)

# Drawing a circle.
cv2.circle(canvas, (150, 150), 50, (255, 0, 0), -1)

cv2.imshow("Canvas", canvas)
cv2.waitKey()