from sr.robot3 import *
robot = Robot()
mtrs = robot.motor_board.motors
ASTEROID_IDS = [i for i in range(150, 200)]

TURNSPEED = 0.2
DRIVESPEED = 0.3
WAIT = 1

def brake():
    '''Sets both motors' power to 0.'''
    mtrs[0].power = 0
    mtrs[1].power = 0

def turn(dir=True):
    if dir: 
        mtrs[0].power = TURNSPEED
        mtrs[1].power = -TURNSPEED
    else:
        mtrs[0].power = -TURNSPEED
        mtrs[1].power = TURNSPEED

def drive():
    mtrs[0].power = DRIVESPEED
    mtrs[1].power = DRIVESPEED


def findTarget(targetid):
    markers = robot.camera.see()
    for marker in markers:
        if marker.id == targetid:
            return marker
    print(f'look couldnt find {targetid}')
    return None


def closestAsteroid(clockwise_turn=True):
    asteroids = []

    while len(asteroids) == 0:
        asteroids = [marker for marker in robot.camera.see() if marker.id in ASTEROID_IDS]
        turn(clockwise_turn)
        robot.sleep(WAIT)
        brake()
        robot.sleep(WAIT)

    closest = None
    for marker in asteroids:
        if closest == None:
            closest = marker
        if marker.position.distance < closest.position.distance:
            closest = marker
    print(closest)
    brake()
    return closest


def turnSee(targetid, clockwise_turn):
    '''
    Scans the surroundings for asteroids, going clockwise.
    Scans to between -0.08 to 0.08 radians
    '''
    print("TUNSEE")
    target_marker = findTarget(targetid)
    while target_marker == None:
        print("Nonefound turnsee")
        turn(clockwise_turn)
        robot.sleep(WAIT/2)
        brake()
        robot.sleep(WAIT)
        target_marker = findTarget(targetid)
        print(target_marker)
    print("correctng")
    while target_marker.position.horizontal_angle < -0.3 or target_marker.position.horizontal_angle > 0.3:
        target_marker = findTarget(targetid)
        turn(clockwise_turn)
        print(target_marker.position.horizontal_angle)
        robot.sleep(WAIT/2)
        brake()
        robot.sleep(WAIT)
    print(f"Found marker, {target_marker}")
    brake()


def asteroidApproach(targetid):
    print("APPROACH")
    '''Approaches the nearest asteroid (the one directly ahead)'''
    target_marker = findTarget(targetid)
    while target_marker:
        target_marker = findTarget(targetid)
        print("driving")
        drive()
        robot.sleep(2*WAIT/3)
        brake()
        robot.sleep(WAIT/3)
    brake()


def main():
    asteroid = closestAsteroid(True)
    robot.sleep(1)
    if turnSee(asteroid.id, False) == -1:
        main()
        return
    robot.sleep(1)
    asteroidApproach(asteroid.id)

main()
