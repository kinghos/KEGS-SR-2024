from sr.robot3 import *
robot = Robot()
mtrs = robot.motor_boards["SR0UK1L"].motors
ASTEROID_IDS = [i for i in range(150, 200)]
ARENA_IDS = [i for i in range(8)]

TURNSPEED = 0.2
DRIVESPEED = 0.3
WAIT = 0.5

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
    print("closestasteroid")
    while len(asteroids) == 0:
        asteroids = [marker for marker in robot.camera.see() if marker.id in ASTEROID_IDS]
        turn(clockwise_turn)
        robot.sleep(WAIT/2)
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


def turnSee(targetid, clockwise_turn, threshold):
    '''
    Scans the surroundings for asteroids, going clockwise.
    Scans to between -0.08 to 0.08 radians
    '''
    print("TUNSEE")
    target_marker = findTarget(targetid)
    while target_marker == None:
        print("Nonefound turnsee")
        turn(clockwise_turn)
        robot.sleep(1.5*WAIT)
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
            turn(True)
        if target_marker.position.horizontal_angle > threshold:
            turn(False)
        print(target_marker.position.horizontal_angle)
        robot.sleep(1.25*WAIT)
        brake()
        robot.sleep(WAIT)
    print(f"Found marker, {target_marker}")
    brake()


def asteroidApproach(targetid):
    print("APPROACH")
    '''Approaches the nearest asteroid (the one directly ahead)'''
    target_marker = findTarget(targetid)
    while target_marker.position.distance > 30:
        target_marker = findTarget(targetid)
        print("driving")
        drive()
        robot.sleep(2*WAIT/3)
        brake()
        robot.sleep(WAIT/3)
        turnSee(target_marker.id, False, 0.2)
    brake()


def approachBase():
    '''Approach the base zone to deposit asteroids'''
    markers = []
    startTime = robot.time()
    found = False
    targetMarker = 0
    while robot.time() - startTime < 10 and not found:
        brake()
        robot.sleep(0.25)
        markers = robot.camera.see()
        minimum = float("inf")
        for marker in markers:
            if marker.id in ARENA_IDS and marker.position.distance < minimum:
                brake()
                print(f"Found base: {marker.id}")
                minimum = marker.position.distance
                found == True
                targetMarker = marker.id
                
        turn(TURNSPEED)

    brake()
    if not found:
        print("Couldn't find base")
        return None
    else:
        while marker.position.horizontal_angle > 0.1:
            marker = targetMarker(targetMarker.id) # FIXME Add checks for None 
            print("Horizontal angle: ", marker.position.horizontal_angle)
            turn(True)
        while marker.position.horizontal_angle < 0.1:
            marker = targetMarker(targetMarker.id) # FIXME Add checks for None 
            print("Horizontal angle: ", marker.position.horizontal_angle)
            turn(False)
        brake()
        print("Aligned with base")
        robot.sleep(0.05)
        marker = targetMarker(targetMarker) # FIXME Add checks for None
        while marker.position.distance > 200:
            marker = targetMarker(targetMarker.id)
            print("Distance: ", marker.position.distance)
            drive()
        return True

def main():
    asteroid = closestAsteroid(True)
    robot.sleep(WAIT)
    if turnSee(asteroid.id, False, 0.1) == -1:
        main()
        return
    robot.sleep(WAIT)
    asteroidApproach(asteroid.id)
    drive()
    robot.sleep(1)
    brake()
    robot.sleep(WAIT)
    mtrs[0].power = 0.3
    robot.sleep(1)
    brake()
    approachBase()


main()