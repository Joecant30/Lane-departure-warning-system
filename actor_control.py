import carla;
import pygame;
import random;
import numpy as np;


#connect to carla and retrieve world
client = carla.Client("localhost", 2000)
client.set_timeout(15.0)
world = client.load_world("Town05")

#enable synchronous mode on server
settings = world.get_settings()
settings.synchronous_mode = True #turn on synchronous mode
settings.fixed_delta_seconds = 0.05 #set frame rate to 20fps
world.apply_settings(settings)

