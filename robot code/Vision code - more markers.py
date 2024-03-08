from sr.robot3 import *
robot = Robot()
mtrs = robot.motor_board.motors
ASTEROID_IDS = [i for i in range(150, 200)]

TURNSPEED = 0.2
DRIVESPEED = 0.3
def brake():
    '''Sets both motors' power to 0.'''
    mtrs[0].power = 0
    mtrs[1].power = 0

def see():
    '''Returns a list of markers seen by the robot's camera. If no markers are seen after 20 seconds, returns None.'''
    markers = []
    startTime = robot.time()
    while not markers:
        markers = robot.camera.see()
        if robot.time() - startTime > 20:
            print("No markers found")
            return None
        robot.sleep(0.05)
    return markers

def asteroidScan():
    '''
    Scans the surroundings for asteroids, going clockwise.
    Scans to between -0.08 to 0.08 radians
    '''
    
    markers = see()
    if markers:
        while markers[0].position.horizontal_angle < -0.1 or markers[0].position.horizontal_angle > 0.1:
            markers = see()
            mtrs[0].power = -TURNSPEED
            mtrs[1].power = TURNSPEED
            print(markers[0].position.horizontal_angle)
            brake()
            robot.sleep(1)
    print(f"Found marker, {markers[0]}")
    brake()

def asteroidApproach():
    '''Approaches the nearest asteroid (the one directly ahead)'''
    markers = see()
    while markers:
        print("driving")
        mtrs[0].power = DRIVESPEED
        mtrs[1].power = DRIVESPEED
    brake()

asteroidScan()
robot.sleep(5)
asteroidApproach()
robot.sleep(5)
