import numpy as np
import cv2
import matplotlib.pyplot as plt

#Perform sobel edge detection and thresholding on the lane image
def threshold_image(img, sx_thresh=(15, 255)):
    #Convert image to greyscale
    grey = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(np.float)

    #Perform Sobel edge detection on x axis of image
    sobel_x64f = cv2.Sobel(grey, cv2.CV_64F, 1, 0, ksize=5)
    abs_sobel_x64f = np.absolute(sobel_x64f) #Absolute of Sobel x details lines perpendicular to horizon
    sobel_x8u = np.uint8(255*abs_sobel_x64f/np.max(abs_sobel_x64f))

    #Threshold x gradient of light channel
    sobel_x_binary = np.zeros_like(sobel_x8u)
    sobel_x_binary[(sobel_x8u >= sx_thresh[0]) & (sobel_x8u <= sx_thresh[1])] = 1

    return sobel_x_binary

def process_image(img):
    return threshold_image(img)
