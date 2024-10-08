import carla
import pygame
import random
import cv2
import numpy as np
import process_image as process
import lane_detection as lane


#---init_world()----


def init_world():
    # connect to carla server and select world
    client = carla.Client("localhost", 2000)
    client.set_timeout(30.0)
    world = client.load_world("Town05")

    # enable synchronous mode on server and set frame rate
    settings = world.get_settings()
    settings.synchronous_mode = True
    settings.fixed_delta_seconds = 0.05
    world.apply_settings(settings)

    return world


#---init_vehicle()----


def init_vehicle(world):
# select Tesla model 3 for use in the sim world
    blueprint_library = world.get_blueprint_library()
    bp = blueprint_library.filter("model3")[0]

    # randomise colour of vehicle
    if bp.has_attribute("colour"):
        colour = random.choice(bp.get_attribute("colour").recommended_values)
        bp.set_attribute("colour", colour)

    # select random spawn point and store it
    spawn_points = world.get_map().get_spawn_points()
    transform = random.choice(spawn_points)

    # spawn vehicle in the world and notify user it's created
    vehicle = world.spawn_actor(bp, transform)
    print("created %s" % vehicle.type_id)

    return vehicle, blueprint_library


#---init_vehicle_sensors()----


def init_vehicle_sensors(world, vehicle, blueprint_library):
    # create a new RGB camera positioned behind the vehicle for user control
    sensor_bp = blueprint_library.find('sensor.camera.rgb')
    sensor_bp.set_attribute("image_size_x", "1280")
    sensor_bp.set_attribute("image_size_y", "720")
    sensor_transform = carla.Transform(carla.Location(x=-5, z=3), carla.Rotation(pitch=-20))
    sensor = world.spawn_actor(sensor_bp, sensor_transform, attach_to=vehicle)
    print("created %s" % sensor.type_id)

    # create a new RGB camera positioned at the front of the vehicle for lane detection
    lane_bp = blueprint_library.find('sensor.camera.rgb')
    lane_bp.set_attribute("image_size_x", "1280")
    lane_bp.set_attribute("image_size_y", "720")
    lane_bp.set_attribute("fov", "100")
    lane_sensor_transform = carla.Transform(carla.Location(x=1.5, z=1.5), carla.Rotation(pitch=-10))
    lane_sensor = world.spawn_actor(lane_bp, lane_sensor_transform, attach_to=vehicle)
    print("created %s" % lane_sensor.type_id)

    # add lane invasion sensors to detect when the vehicle crosses markings
    lane_invasion_bp = blueprint_library.find("sensor.other.lane_invasion")
    lane_invasion_sensor = world.spawn_actor(lane_invasion_bp, carla.Transform(), attach_to=vehicle)
    print("created %s" % lane_invasion_sensor.type_id)

    return sensor, lane_sensor, lane_invasion_sensor


#---RenderObject----


class RenderObject(object):
    # initialise and render object to pass to the PyGame surface
    def __init__(self, width, height):
        init_image = np.random.randint(0, 255, (height, width, 3), dtype="uint8")
        self.surface = pygame.surfarray.make_surface(init_image.swapaxes(0, 1))


#---get_text_dimensions()----


def get_text_dimensions(img, text, font):
    # calculate where the vehicle information on the lane screen should be centred
    text_size = cv2.getTextSize(text, font, 1, 2)
    text_x = (img.shape[1] - text_size[0][0]/2)/2
    return text_x


#---vehicle_control_callback()----


def vehicle_control_callback(data, obj):
    # reshape raw rgb sensor data
    # display rgb data to the window
    img = np.reshape(np.copy(data.raw_data), (data.height, data.width, 4))
    img = img[:,:,:3]
    img = img[:, :, ::-1]
    obj.surface = pygame.surfarray.make_surface(img.swapaxes(0,1))


#---lane_detection_callback()----


def lane_detection_callback(data, lane_obj, perspective_obj, sliding_obj, veh, sensor_image_w, sensor_image_h):
    # reshape raw rgb sensor data
    # call process_image to warp the image and display it to window
    img = np.reshape(np.copy(data.raw_data), (data.height, data.width, 4))
    img_ = process.process_image(img, sensor_image_h, sensor_image_w)
    perspective_obj.surface = pygame.surfarray.make_surface(img_.swapaxes(0,1))
    img = img[:,:,:3]
    img = img[:, :, ::-1]

    # perform lane detection and display results to the window
    output_windows, curves, lanes = lane.sliding_window(img_)
    sliding_obj.surface = pygame.surfarray.make_surface(output_windows.swapaxes(0,1)) 
    curve_radius = lane.find_curve(img_, curves[0], curves[1])
    lanes = lane.draw_lines(img, curves[0], curves[1], sensor_image_h, sensor_image_w)

    # add vehicle information to the lane display
    font = cv2.FONT_HERSHEY_DUPLEX
    font_colour = (0, 0, 0)
    font_size = 0.5
    avg_lane_curve = np.mean([curve_radius[0], curve_radius[1]])

    veh_offset_text = "Dist. from center: {:.4f} m".format(curve_radius[2])
    veh_offset_x = get_text_dimensions(lanes, veh_offset_text, font)

    lane_curve_text = "Lane curvature: {:.0f} m".format(avg_lane_curve)
    lane_curve_x = get_text_dimensions(lanes, lane_curve_text, font)

    vehicle_speed_text = "Vehicle speed: {:.1f}".format(veh.get_velocity().length()*2.237) + " mph"
    vehicle_speed_x = get_text_dimensions(lanes, vehicle_speed_text, font)

    cv2.putText(lanes, veh_offset_text, (int(veh_offset_x), 710), font, font_size, font_colour, 1)
    cv2.putText(lanes, lane_curve_text, (int(lane_curve_x), 690), font, font_size, font_colour, 1)
    cv2.putText(lanes, vehicle_speed_text, (int(vehicle_speed_x), 670), font, font_size, font_colour, 1)
    lane_obj.surface = pygame.surfarray.make_surface(lanes.swapaxes(0,1))


#---lane_departure_callback()----


def lane_departure_callback(event, invasion_obj, control_obj):
    # create list containing the lane type involved in collision
    lane_types = set(x.type for x in event.crossed_lane_markings)
    lane_text = ['%r' % str(x).split()[-1] for x in lane_types]
    print(f"Collision at: {lane_text[0]}")

    #initialise warning sound
    warning_sound = pygame.mixer.Sound("car-beeping-2.wav")

    # if the blinkers are off then display the warning and play the warning sound
    if control_obj._blinker_active == False:
        image = pygame.image.load("warning_icon.png")
        invasion_obj.set_alpha(255)
        invasion_obj.blit(image, (10,10))
        pygame.mixer.Sound.play(warning_sound)
        

#---ControlObject----


class ControlObject(object):
    #control object to manage vehicle control
    def __init__(self, veh):
        #attributes to store the control state
        self._vehicle = veh
        self._steer = 0
        self._throttle = False
        self._brake = False
        self._steer = None
        self._steer_cache = 0
        self._blinker_active = False

        # the carla.VehicleControl() is needed to alter the vehicles control state
        self._control = carla.VehicleControl()

    # check for keypress events in PyGame window and define the control state
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
            #check if the blinker is already active when key pressed
            if event.key == pygame.K_q:
                if self._blinker_active == False:
                    self._vehicle.set_light_state(carla.VehicleLightState.LeftBlinker)
                    self._blinker_active = True
                else:
                    self._vehicle.set_light_state(carla.VehicleLightState.NONE)
                    self._blinker_active = False
            if event.key == pygame.K_e:
                if self._blinker_active == False:
                    self._vehicle.set_light_state(carla.VehicleLightState.RightBlinker)
                    self._blinker_active = True
                else:
                    self._vehicle.set_light_state(carla.VehicleLightState.NONE)
                    self._blinker_active = False
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
        # apply the control parameters to the vehicle
        self._vehicle.apply_control(self._control)


#---game_loop()----


def game_loop(world, veh, sensor, lane_sensor, lane_invasion_sensor, sensor_image_w, sensor_image_h):

    # instantiate objects for rendering and vehicle control
    renderObject = RenderObject(sensor_image_w, sensor_image_h)
    renderLaneObject = RenderObject(sensor_image_w, sensor_image_h)
    renderPerspectiveObject = RenderObject(sensor_image_w, sensor_image_h)
    renderSlidingObject = RenderObject(sensor_image_w, sensor_image_h)
    renderLaneInvasionObject = pygame.Surface((sensor_image_w, sensor_image_h), pygame.SRCALPHA, 32)
    controlObject = ControlObject(veh)

    # start RGB sensors with PyGame callback
    sensor.listen(lambda image: vehicle_control_callback(image, renderObject))
    lane_sensor.listen(lambda image: lane_detection_callback(image, renderLaneObject, renderPerspectiveObject, renderSlidingObject, veh, sensor_image_w, sensor_image_h))

    # start lane invasion sensor with PyGame callback
    lane_invasion_sensor.listen(lambda event: lane_departure_callback(event, renderLaneInvasionObject, controlObject))

    # initialise PyGame window
    pygame.init()
    gameDisplay = pygame.display.set_mode((sensor_image_w*2,sensor_image_h*2), pygame.HWSURFACE | pygame.DOUBLEBUF)
    gameDisplay.blit(renderObject.surface, (0,0))
    gameDisplay.blit(renderLaneInvasionObject, (0,0))
    gameDisplay.blit(renderLaneObject.surface, (sensor_image_w, 0))
    gameDisplay.blit(renderPerspectiveObject.surface, (0, sensor_image_h))
    gameDisplay.blit(renderSlidingObject.surface, (sensor_image_w, sensor_image_h))
    pygame.display.flip()

    # game loop
    crashed = False
    while not crashed:

        # advance the simulation time
        world.tick()

        # update the display
        gameDisplay.blit(renderObject.surface, (0,0))
        gameDisplay.blit(renderLaneInvasionObject, (0,0))
        gameDisplay.blit(renderLaneObject.surface, (sensor_image_w, 0))
        gameDisplay.blit(renderPerspectiveObject.surface, (0, sensor_image_h))
        gameDisplay.blit(renderSlidingObject.surface, (sensor_image_w, sensor_image_h))
        pygame.display.flip()

        # fade out lane invasion symbol over time
        renderLaneInvasionObject.set_alpha(renderLaneInvasionObject.get_alpha())
        if(renderLaneInvasionObject.get_alpha() == 0):
            pass
        else:
            renderLaneInvasionObject.set_alpha(renderLaneInvasionObject.get_alpha() - 2)

        # process the current control state
        controlObject.process_control()

        # collect key press events
        for event in pygame.event.get():

            # if the window is closed, break the while loop
            if event.type == pygame.QUIT:
                crashed = True

            # parse effect of key press event on control state
            controlObject.parse_control(event)
    
    sensor.stop()
    lane_sensor.stop()
    lane_invasion_sensor.stop()
    pygame.quit()


#---main()----


def main():
    world = init_world()
    vehicle, bp_library = init_vehicle(world)
    sensor, lane_sensor, lane_invasion_sensor = init_vehicle_sensors(world, vehicle, bp_library)
    game_loop(world, vehicle, sensor, lane_sensor, lane_invasion_sensor, 1280, 720)


if __name__ == "__main__":
    main()
