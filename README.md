# Lane Departure Warning System using CARLA

## Overview

A Lane Departure Warning System is an automotive safety feature that warns drivers when they unintentionally depart from or are about to depart from a lane without their indicators active. Road markings are essential for controlling the flow of traffic on busy roads and changing lanes without checking first can cause major incidents.

I have implemented a Lane Departure Warning System that works in real-time using Python and other useful libraries such as OpenCV, NumPy and PyGame. Due to my inability to develop this software using a real vehicle, I have also used CARLA simulator to replicate a realistic physical environment to test and develop my software. CARLA provides a fast and accurate physics engine based on Unreal Engine 4 and also provides a suite of vehicles, sensors and other useful features.

The system will allow a user to control a vehicle in the simulator using PyGame, and the Lane Departure Warning System will work alongside at the same time as the vehicle, overlaying the results as the vehicle moves.

## Technologies

I have used a number of relevant technologies and algorithms to implement this system. The current pipeline of these technologies includes:

- Sobel edge detection
- Gaussian filtering
- Perspective warping
- Sliding window algorithm
- Histogram peak detection
- Curve fitting
- Overlay bound lane region
- Display real-time lane detection

My decision to use these technologies has been mostly down to their time efficiency of them compared to the alternative options. For example, Sobel edge detection is much less complex than Canny edge detection and provides little benefit over Sobel operators for this application. Unlike other implementations of similar software I have seen, this project aims to achieve real-time lane detection compared to lane detection over pre-made images or videos. 

Furthermore, these technologies provide robustness, with algorithms like the sliding window search being able to easily detect curved lane markings while still being efficient at doing so.

## Challenges

It should be noted that a powerful GPU is required to run CARLA. CARLA recommends a graphics card with at least 6GB of VRAM, however, they suggest a card with 8GB would be more beneficial for smoother performance. This can be limiting when trying to run it on any machine, as a powerful computer will be required to run this software. In reality the software would be used ina real vehicle and so VRAM requirements wouldn't be a concern.

## System requirements

- 8GB VRAM
- 20GB disk space
- Windows 10/MacOS/Linux

## How to install

### Carla

Before installing the correct libraries for this project you will first need to download the correct version of CARLA from their repository. The repository can be found at https://github.com/carla-simulator/carla/blob/master/Docs/download.md where you can download the correct version for your operating system.

Once the file has been downloaded, extract it and inspect the contents. The CarlaUE4.exe application is what you will need to have running in the background when you run the software.

To make launching the .exe file easier it is possible to create a .bat file for Windows or a shell script for Linux to launch it automatically without searching for it. You can use `path_to_Carla/CarlaUE4.exe -carla-server` to run every time you run the script.


### Python environment

For this software, we will be using the downloadable Python package for carla which works up to Python 3.8 or 2.7. It can be a good idea to look up how to set up a virtual environment in your IDE so that you don't have conflicts with Python versions on your computer.

Within the environment or IDE, you can now update which version of pip you have with `pip3 install --upgrade pip` for Python 3 and just use pip for Python 2.

Once you have done this you should be able to install PyGame and NumPy using `pip3 install --user pygame numpy` for Windows or `pip install --user pygame numpy && pip3 install --user pygame numpy` for Linux

To download OpenCV use the same command regardless of operating system with `pip3 install opencv-python` 

Finally, download the carla package using `pip3 install carla` to gain access to the carla Python API.

I sometimes found that using pip3 or python3 commands while using Python 3.8 didn't work, so try using normal pip or Python if this happens.

## How to use

Before you use the program you might want to go into the `main.py` file and in the `init_vehicle_sensors()` function near the top change the width and height attributes of the sensors from 1280x720 to whatever one-quarter of your screen resolution is.

Once you have set up the program correctly you can run main.py while CarlaUE4.exe is running in the background. A Pygame window should appear with the 4 screens displaying the sensor data. If it doesn't load and times out then just try again, sometimes it can take a little longer.

You will be able to control the vehicle on the top left screen using your keyboard. The following key binds are as follows:

- Turn left and right: A and D 
- Accelerate and brake: W and S
- Left indicator and right indicator: Q and E