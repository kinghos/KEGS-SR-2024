from sr.robot3 import *
robot = Robot()
mtrs = robot.motor_boards["SR0UK1L"].motors
ASTEROID_IDS = [i for i in range(150, 200)]
BASE_IDS = [i for i in range(8)]

TURNSPEED = 0.22
DRIVESPEED = 0.3
WAIT = 0.4

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

def reverse():
    mtrs[0].power = -DRIVESPEED
    mtrs[1].power = -DRIVESPEED


def findTarget(targetid):
    markers = robot.camera.see()
    for marker in markers:
        if marker.id == targetid:
            return marker
    print(f'look couldnt find {targetid}')
    return None


def closestMarker(clockwise_turn=True, type=ASTEROID_IDS):
    markers = []
    print("closestMarker")
    while len(markers) == 0:
        markers = [marker for marker in robot.camera.see() if marker.id in type]
        turn(clockwise_turn)
        robot.sleep(1.5*WAIT)
        brake()
        robot.sleep(WAIT)

    closest = None
    for marker in markers:
        if closest == None:
            closest = marker
        if marker.position.distance < closest.position.distance:
            closest = marker
    print(closest)
    brake()
    return closest


def turnSee(targetid, clockwise_turn, threshold):
    '''
    Scans the surroundings for asteroids, going clockwise.
    Scans to between -0.08 to 0.08 radians
    '''
    print("turnsee")
    target_marker = findTarget(targetid)
    while target_marker == None:
        print("Nonefound turnsee")
        turn(clockwise_turn)
        robot.sleep(WAIT)
        brake()
        robot.sleep(WAIT)
        target_marker = findTarget(targetid)
        print(target_marker)
    print("correctng")
    while target_marker.position.horizontal_angle < -threshold or target_marker.position.horizontal_angle > threshold:
        target_marker = findTarget(targetid)
        if target_marker == None:
            return -1
        if target_marker.position.horizontal_angle < -threshold:
            turn(False)
        if target_marker.position.horizontal_angle > threshold:
            turn(True)
        print(target_marker.position.horizontal_angle)
        robot.sleep(1.25*WAIT)
        brake()
        robot.sleep(WAIT)
    print(f"Found marker, {target_marker}")
    brake()


def markerApproach(targetid, distance=600, threshold=0.05):
    print("APPROACH")
    '''Approaches the nearest asteroid (the one directly ahead)'''
    target_marker = findTarget(targetid)
    if target_marker == None:
        return -1
    while target_marker.position.distance > distance:
        target_marker = findTarget(targetid)
        if target_marker == None:
            return -1
        if target_marker.position.distance <= distance:
            break
        print("driving")
        drive()
        robot.sleep(WAIT)
        brake()
        robot.sleep(WAIT)
        turnSee(target_marker.id, False, threshold)
    brake()


def main():
    print("START")
    asteroid = closestMarker(True, ASTEROID_IDS)
    robot.sleep(WAIT)
    if turnSee(asteroid.id, False, 0.1) == -1:
        main()
        return
    if markerApproach(asteroid.id) == -1:
        main()
        return
    drive()
    robot.sleep(3)
    brake()
    robot.sleep(WAIT)
    mtrs[0].power = 0.3
    robot.sleep(0.5)
    brake()
    base = closestMarker(True, BASE_IDS)
    if turnSee(base.id, False, 0.2) == -1:
        main()
        return
    while markerApproach(base.id, 750, 0.3) == -1:
        markerApproach(base.id)
    drive()
    robot.sleep(1)
    brake()
    robot.sleep(WAIT)
    reverse()

while True:
    main()