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

def turn():
    mtrs[0].power = TURNSPEED
    mtrs[1].power = TURNSPEED

def drive():
    mtrs[0].power = TURNSPEED
    mtrs[1].power = TURNSPEED


def findTarget(targetid):
    markers = robot.camera.see()
    for marker in markers:
        if marker.id == targetid:
            return marker
    print(f'look couldnt find {targetid}')
    return None


def closestAsteroid():
    asteroids = []

    while len(asteroids) == 0:
        asteroids = [marker for marker in robot.camera.see() if marker in ASTEROID_IDS]
        turn()

    closest = None
    for marker in asteroids:
        if closest == None:
            closest = marker
        if marker.position.distance < closest.position.distance:
            closest = marker
    
    return closest


def turnSee(targetid):
    '''
    Scans the surroundings for asteroids, going clockwise.
    Scans to between -0.08 to 0.08 radians
    '''
    target_marker = findTarget(targetid)
    while target_marker.position.horizontal_angle < -0.1 or target_marker.position.horizontal_angle > 0.1:
        target_marker = findTarget(targetid)
        mtrs[0].power = -TURNSPEED
        mtrs[1].power = TURNSPEED
        print(target_marker.position.horizontal_angle)
        brake()
        robot.sleep(1)
    print(f"Found marker, {target_marker}")
    brake()


def asteroidApproach(targetid):
    '''Approaches the nearest asteroid (the one directly ahead)'''
    target_marker = findTarget(targetid)
    while target_marker:
        print("driving")
        mtrs[0].power = DRIVESPEED
        mtrs[1].power = DRIVESPEED
    brake()


def main():
    asteroid = closestAsteroid()
    robot.sleep(5)
    turnSee(asteroid)
    robot.sleep(5)
    asteroidApproach(asteroid)

main()