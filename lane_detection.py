import numpy as np
import cv2
import matplotlib.pyplot as plt

def sliding_window(img):
    num_windows = 9
    margin = 125
    minpix = 1
    window_height = np.int(img.shape[0]/num_windows)

def detect_lanes(img):
    left_lane_indices = []
    right_lane_indices = []
    sliding_window(img)
