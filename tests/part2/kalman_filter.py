# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 12:53:59 2023
KALMAN FILTER MODIFIED    working
@author: naray
"""
import numpy as np
import cv2

global A,B,H,Q,R,P
# global x1,y1,x2,y2

def predict(A,B,x,u,P,Q):   
    # Update states           
    x = np.dot(A,x) + np.dot(B, u)  #x_k =Ax_(k-1) + Bu_(k-1)       
    # Calculate error covariance
    P = np.dot(np.dot(A,P), A.T) + Q  # P= A*P*A' + Q     
    return x

def update(H,x,P,R, z):  
    S = np.dot(H, np.dot(P, H.T)) + R   # S = H*P*H'+R
    K = np.dot(np.dot(P, H.T), np.linalg.inv(S)) # K = P * H'* inv(H*P*H'+R)   
    x = np.round(x + np.dot(K,(z - np.dot(H, x))))  # Estimate x
    x=([x[0,0],x[1,1],0,0])    
    I = np.eye(H.shape[1])
    # Update error covariance matrix
    P = (I - (K * H)) * P     
    return x    

# Define sampling time
dt = 1
u_x = 1
u_y = 1
std_acc = 1
x_std_meas=0.1
y_std_meas=0.1
# Define the  control input variables
u = np.matrix([[u_x],[u_y]])
# Intial State
x = np.matrix([[0],[0],[0],[0]])

# Define the State Transition Matrix A
A = np.matrix([[1, 0, dt, 0],
                    [0, 1, 0, dt],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1]])
# Define the Control Input Matrix B
B = np.matrix([[(dt**2)/2, 0],
                    [0, (dt**2)/2],
                    [dt,0],
                    [0,dt]])
# Define Measurement Mapping Matrix
H = np.matrix([[1, 0, 0, 0],
                    [0, 1, 0, 0]])
#Initial Process Noise Covariance
Q = np.matrix([[(dt**4)/4, 0, (dt**3)/2, 0],
                    [0, (dt**4)/4, 0, (dt**3)/2],
                    [(dt**3)/2, 0, dt**2, 0],
                    [0, (dt**3)/2, 0, dt**2]]) * std_acc**2
#Initial Measurement Noise Covariance
R = np.matrix([[x_std_meas**2,0],[0, y_std_meas**2]])
#Initial Covariance Matrix
P = np.eye(A.shape[1]) 

# Create opencv video capture object
VideoCap = cv2.VideoCapture('MovBall.MOV')

def find_center(hsv):
    h,s,v = cv2.split(hsv)
    ret,thresh = cv2.threshold(s,100,255,0) # No noise, the ball should be correctly and accurately centered.
    M = cv2.moments(thresh)
    cx = int(M['m10']/M['m00']) # Sum of mi*xi/sum of mi
    cy=int(M['m01']/M['m00'])   # Sum of mi*yi/sum of mi
    center=[cx,cy]
    return center       
while(True):
       # Read frame
       ret, frame = VideoCap.read()
       # Detect object, by reading frame by frame
       hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
       center = find_center(hsv) # Getting the center the ball.

        # dev is used to confuse the filter. Why? This is because we want to check how accurate and correct the algorithm is.
        # Also, we are not exactly sure if center is the center of the ball, but exact measurement is not needed, just approximate.
        # Even with such a large noise deviation (in the range -20, ,30), the Kalman filter should work despite this 50px error term in x and y direction.
       dev=np.random.randint(-20,30) # Large error in observation is added
       z=[center[0]+dev,center[1]-dev]
       cv2.circle(frame,center, 10, (255,0, 0), 2)  # Draw a blue circle at the center of the ball.
       # Predict
       x=predict(A,B,x,u,P,Q)
       (x1,y1)=(x[0],x[1])
       # Draw a rectangle as the predicted object position        
       cv2.rectangle(frame, (int(x1 - 5), int(y1 - 5)), (int(x1 + 5), int(y1 + 5)), (0, 0, 255), 2)
       x=update(H,x,P,R,z)
       (x2,y2) = (x[0],x[1])  
       cv2.rectangle(frame, (int(x2 - 5), int(y2 - 5)), (int(x2 + 5), int(y2 + 5)), (255, 255, 255), 2)   
       # Actuation components have been made 0.
       x=np.matrix([[x2],[y2],[0],[0]])
       cv2.imshow('image',frame) 
       k = cv2.waitKey(30) & 0xff
       if k == 27:
           break
VideoCap.release()
cv2.destroyAllWindows()   