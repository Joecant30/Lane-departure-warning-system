import numpy as np
import cv2
import matplotlib.pyplot as plt

def histogram_values(img):
    hist = np.sum(img[img.shape[0]//2:,:], axis=0)
    return hist

def sliding_window(img):
    num_windows = 9
    margin = 50
    minpix = 1

    #calculate histogram peaks of image halves
    histogram = histogram_values(img)
    midpoint = int(histogram.shape[0]/2)
    leftx_initial = np.argmax(histogram[:midpoint])
    rightx_initial = np.argmax(histogram[:midpoint]) + midpoint

    #set height of sliding window
    window_height = np.int(img.shape[0]/num_windows)

    #get x and y location of all non-zero pixels in the image
    nonzero = img.nonzero()
    nonzero_y = np.array(nonzero[0])
    nonzero_x = np.array(nonzero[1])

    #set current left and right peaks to initial peaks
    leftx_current = leftx_initial
    rightx_current = rightx_initial

    #empty arrays to store pixel indices of lane lines
    left_lane_indices = []
    right_lane_indices = []

    