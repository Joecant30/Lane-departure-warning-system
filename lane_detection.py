import numpy as np
import cv2
import matplotlib.pyplot as plt

def process_image(img):
    img = cv2.cvtColor(img, cv2.COLOR_RGB2HLS)
    return img
