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

#select random vehicle from blueprint library
blueprint_library = world.get_blueprint_library()
bp = random.choice(blueprint_library.filter("vehicle"))

#randomise colour of vehicle
if bp.has_attribute("colour"):
    colour = random.choice(bp.get_attribute("colour").recommended_values)
    bp.set_attribute("colour", colour)

#select random spawn point and store it
spawn_points = world.get_map().get_spawn_points()
transform = random.choice(spawn_points)

#spawn vehicle in the world and notify user it's created
vehicle = world.spawn_actor(bp, transform)
print("created %s" % vehicle.type_id)

#create a new RGB camera and position it relative to the car
sensor_bp = blueprint_library.find('sensor.camera.rgb')
sensor_transform = carla.Transform(carla.Location(x=1.5, z=2.4), carla.Rotation(pitch=-20))
sensor = world.spawn_actor(sensor_bp, sensor_transform, attach_to=vehicle)
print("created %s" % sensor.type_id)

