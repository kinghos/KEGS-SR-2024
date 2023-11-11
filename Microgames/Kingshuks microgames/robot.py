from sr.robot3 import *

robot = Robot()
mtrs = robot.motor_board.motors
duino = robot.arduino
duino.pins[2].mode = INPUT
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

def identifyMarker(markerType):
    '''Finds a certain type of marker in the camera feed, and returns its index'''
    markers = robot.camera.see()
    for marker in markers:
        if marker.id in ASTEROID_IDS:
            return markers.index(marker)

def asteroidApproach():
    '''Approaches the nearest asteroid (the one directly ahead)'''
    markers = robot.camera.see()
    while markers[0].position.distance > 30:
        mtrs[0].power = 0.4
        mtrs[1].power = 0.4

mtrs[0].power = -0.3
mtrs[1].power = -0.3

# Retreat to back wall; begin alighnment
while not duino.pins[2].digital_read():
    robot.sleep(0.1)
brake()

markers = robot.camera.see()
while markers[0].position.horizontal_angle < -0.02 and markers[0].position.horizontal_angle > -0.02:
    markers = robot.camera.see()
    mtrs[0].power = 0.1
    mtrs[1].power = -0.1

asteroidScan()
asteroidApproach()
