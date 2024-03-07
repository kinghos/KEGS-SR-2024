from sr.robot3 import *
robot = Robot()
mtrs = robot.motor_board.motors
ASTEROID_IDS = [i for i in range(150, 200)]

TURNSPEED = 0.25
DRIVESPEED = 0.4
def brake():
    '''Sets both motors' power to 0.'''
    mtrs[0].power = 0
    mtrs[1].power = 0

def see():
    markers = []
    startTime = robot.time()
    while not markers:
        markers = robot.camera.see()
        robot.sleep(0.05)
        if time.time() - startTime > 20:
            print("No markers found")
            return None
    return markers

def asteroidScan():
    '''
    Scans the surroundings for asteroids, going clockwise.
    Scans to between -0.02 to 0.02 radians
    '''
    
    markers = see()
    if markers:
        while markers[0].position.horizontal_angle < -0.02 and markers[0].position.horizontal_angle > -0.02:
            markers = see()
            mtrs[0].power = TURNSPEED
            mtrs[1].power = -TURNSPEED
    
    brake()

def asteroidApproach():
    '''Approaches the nearest asteroid (the one directly ahead)'''
    markers = see()
    if markers:
        while markers[0].position.distance > 30:
            mtrs[0].power = DRIVESPEED
            mtrs[1].power = DRIVESPEED
    brake()

asteroidScan()
asteroidApproach()
