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
bp = blueprint_library.filter("model3")[0]

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

#create a new RGB camera positioned behind the vehicle for user control
sensor_bp = blueprint_library.find('sensor.camera.rgb')
sensor_transform = carla.Transform(carla.Location(x=-5, z=3), carla.Rotation(pitch=-20))
sensor = world.spawn_actor(sensor_bp, sensor_transform, attach_to=vehicle)
print("created %s" % sensor.type_id)

#create a new RGB camera positioned at the front of the vehicle for lane detection
lane_sensor_transform = carla.Transform(carla.Location(x=1.8, z=1.5), carla.Rotation(pitch=-20))
lane_sensor = world.spawn_actor(sensor_bp, lane_sensor_transform, attach_to=vehicle)
print("created %s" % lane_sensor.type_id)

#create and render object to pass to the PyGame surface
class RenderObject(object):
    def __init__(self, width, height):
        init_image = np.random.randint(0, 255, (height, width, 3), dtype="uint8")
        self.surface = pygame.surfarray.make_surface(init_image.swapaxes(0, 1))

#camera sensor callback function, reshapes raw data from the sensor into 2D RGB and applies to PyGame surface
def pygame_callback(data, obj):
    img = np.reshape(np.copy(data.raw_data), (data.height, data.width, 4))
    img = img[:,:,:3]
    img = img[:, :, ::-1]
    obj.surface = pygame.surfarray.make_surface(img.swapaxes(0,1))

#control object to manage vehicle control
class ControlObject(object):
    def __init__(self, veh):
        #attributes to store the control state
        self._vehicle = veh
        self._steer = 0
        self._throttle = False
        self._brake = False
        self._steer = None
        self._steer_cache = 0

        #the carla.VehicleControl() is needed to alter the vehicles control state
        self._control = carla.VehicleControl()

    #check for keypress events in PyGame window and define the control state
    def parse_control(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._vehicle.set_autopilot(False)
            if event.key == pygame.K_w:
                self._throttle = True
            if event.key == pygame.K_s:
                self._brake = True
            if event.key == pygame.K_d:
                self._steer = 1 
            if event.key == pygame.K_a:
                self._steer = -1 
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                self._throttle = False
            if event.key == pygame.K_s:
                self._brake = False
                self._control.reverse = False
            if event.key == pygame.K_d:
                self._steer = None
            if event.key == pygame.K_a:
                self._steer = None

    # process the current control state, change the control parameter
    # if the key remains pressed
    def process_control(self):

        if self._throttle:
            # limit top speed to 15mph for better actor control
            if self._vehicle.get_velocity().length() > 6.71:
                self._control.throttle = 0.33
                self._control.gear = 1
                self._control.brake = False
            else:
                self._control.throttle = min(self._control.throttle + 0.01, 1)
                self._control.gear = 1
                self._control.brake = False
        elif not self._brake:
            self._control.throttle = 0.0

        if self._brake:
            # if the down arrow is held down when the car is stationary, switch to reverse
            if self._vehicle.get_velocity().length() < 0.01 and not self._control.reverse:
                self._control.brake = 0.0
                self._control.gear = 1
                self._control.reverse = True
                self._control.throttle = min(self._control.throttle + 0.1, 1)
            elif self._control.reverse:
                self._control.throttle = min(self._control.throttle + 0.1, 1)
            else:
                self._control.throttle = 0.0
                self._control.brake = min(self._control.brake + 0.3, 1)
        else:
            self._control.brake = 0.0

        if self._steer is not None:
            if self._steer == 1:
                self._steer_cache += 0.02
            if self._steer == -1:
                self._steer_cache -= 0.02
            min(0.7, max(-0.7, self._steer_cache))
            self._control.steer = round(self._steer_cache,1)
        else:
            if self._steer_cache > 0.0:
                self._steer_cache *= 0.2
            if self._steer_cache < 0.0:
                self._steer_cache *= 0.2
            if 0.01 > self._steer_cache > -0.01:
                self._steer_cache = 0.0
            self._control.steer = round(self._steer_cache,1)

        #apply the control parameters to the vehicle
        self._vehicle.apply_control(self._control)

#get sensor dimensions
sensor_image_w = sensor_bp.get_attribute("image_size_x").as_int()
sensor_image_h = sensor_bp.get_attribute("image_size_y").as_int()

#instantiate objects for rendering and vehicle control
renderObject = RenderObject(sensor_image_w, sensor_image_h)
renderLaneObject = RenderObject(sensor_image_w, sensor_image_h)
controlObject = ControlObject(vehicle)

#start sensor with PyGame callback
sensor.listen(lambda image: pygame_callback(image, renderObject))
lane_sensor.listen(lambda image: pygame_callback(image, renderLaneObject))

#initialise PyGame window
pygame.init()
gameDisplay = pygame.display.set_mode((sensor_image_w*2,sensor_image_h), pygame.HWSURFACE | pygame.DOUBLEBUF)
# draw black to the display
gameDisplay.fill((0,0,0))
gameDisplay.blit(renderObject.surface, (0,0))
gameDisplay.blit(renderLaneObject.surface, (sensor_image_w, 0))
pygame.display.flip()

#game loop
crashed = False

while not crashed:
    #advance the simulation time
    world.tick()
    #update the display
    gameDisplay.blit(renderObject.surface, (0,0))
    gameDisplay.blit(renderLaneObject.surface, (sensor_image_w, 0))
    pygame.display.flip()
    #process the current control state
    controlObject.process_control()
    #collect key press events
    for event in pygame.event.get():
        #if the window is closed, break the while loop
        if event.type == pygame.QUIT:
            crashed = True

        #parse effect of key press event on control state
        controlObject.parse_control(event)
        
sensor.stop()
pygame.quit()

