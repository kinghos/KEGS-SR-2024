from sr.robot3 import *
robot = Robot()
mtrs = robot.motor_board.motors
ASTEROID_IDS = [i for i in range(150, 200)]

def brake():
    '''Sets both motors' power to 0.'''
    mtrs[0].power = 0
    mtrs[1].power = 0

def asteroidScan():
    '''
    Scans the surroundings for asteroids, going clockwise.
    Scans to between -0.02 to 0.02 radians
    '''
    markers = robot.camera.see()
    while markers[0].position.horizontal_angle < -0.02 and markers[0].position.horizontal_angle > -0.02:
        markers = robot.camera.see()
        mtrs[0].power = 0.1
        mtrs[1].power = -0.1
    brake()

def asteroidApproach():
    '''Approaches the nearest asteroid (the one directly ahead)'''
    markers = robot.camera.see()
    while markers[0].position.distance > 30:
        mtrs[0].power = 0.4
        mtrs[1].power = 0.4

while True:
    asteroidScan()
    asteroidApproach()

    # Turn 90 degrees (needs tweaking)
    mtrs.power[0] = 0.4
    mtrs.power[1] = -0.4

    robot.sleep(2)
    mtrs.power[0] = 0.2
    mtrs.power[1] = 0.2
    robot.sleep(1)
    brake()

