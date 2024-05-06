from sr.robot3 import *
from math import pi
from random import randint

robot = Robot()
mtrs = robot.motor_boards["SR0UK1L"].motors # driving motors
"""
 Looking from birds eye with it facing forwards, motor 0 is the right motor, motor 1 is the left (dodgy connection)"""
mech_board = robot.motor_boards["SR0KJ15"].motors
uno = robot.arduino

iteration_no = 0 # number of iterations of main while loop

CPR = 2 * pi * 1000/ (4*11 * 0.229) # Magic functioning as of 19.03.24
WHEEL_DIAMETER = 80
ASTEROID_IDS = [i for i in range(150, 200)] #this isn't actually a constant as we remove asteroids for a blacklist
BASE_IDS = [i for i in range(robot.zone * 7, (robot.zone + 1) * 7)] # To change zone click settings on robot.lan (defaults to 0)
NUMBER_OF_WALL_MARKERS = 28
EGG_ID = 110
PORT_ID = robot.zone + 120
STARBOARD_ID = robot.zone + 125

TURNSPEED = 0.17
DRIVESPEED = 0.3
WAIT = 0.2

UPPER_THRESHOLD_CURRENT = 1.5 # Amps - current too high
# MED_THRESHOLD_CURRENT = 0.85
# LOWER_THRESHOLD_CURRENT = 0.2 # current too low

print(BASE_IDS)
#uno.pins[2].mode = INPUT
#uno.pins[3].mode = INPUT #not used anymore
uno.pins[7].mode = INPUT_PULLUP

def brake():
    '''Sets both motors' power to 0.'''
    mtrs[0].power = 0
    mtrs[1].power = 0

def turn(clockwise=True, speed_level=0):
    '''Speed level: defaults to 0, added to the default turnspeed'''
    if clockwise: 
        mtrs[0].power = -((TURNSPEED + speed_level) % 1)
        mtrs[1].power = ((2*(TURNSPEED + speed_level)) % 1) # ×2 helps both motors turn so we turn on the spot
    else:
        mtrs[0].power = ((2*(TURNSPEED + speed_level)) % 1)
        mtrs[1].power = -((TURNSPEED + speed_level) % 1)

def drive(speed_level=0):
    '''Speed level: defaults to 0, added to the default turnspeed'''
    mtrs[0].power = (DRIVESPEED+speed_level) % 1 
    mtrs[1].power = (DRIVESPEED+speed_level) % 1 + 0.03

def reverse(speed_level=0):
    '''Speed level: defaults to 0, added to the default turnspeed'''
    mtrs[0].power = -(DRIVESPEED+speed_level) 
    mtrs[1].power = -(DRIVESPEED+speed_level) - 0.03

def findTarget(targetid):
    '''Identify a marker based on its ID. Return the marker object if found, else return None.'''
    markers = robot.camera.see()
    for marker in markers:
        if marker.id == targetid:
            return marker
    print(f"findTarget couldn't find {targetid}")
    return None

def closestMarker(clockwise_turn, markerType):
    '''
    Returns the first marker it sees whilst turning
    Returns None if not found / timeout
    '''
    print("closestMarker")
    markers = []
    startTime = robot.time()
    TIMEOUT = 20

    if markerType == BASE_IDS:
        print("closestMarker with base")

    while len(markers) == 0 and robot.time() - startTime < TIMEOUT:
        markers = [marker for marker in robot.camera.see() if marker.id in markerType]
        if len(markers) > 0:
            break
        turn(clockwise_turn)
        checkStuck()
        robot.sleep(2.5*WAIT)
        brake()
        robot.sleep(1.5*WAIT)

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
    Scans the surroundings for targetid marker, going clockwise (clockwise_turn = True) or anticlockwise (clockwise_turn = False).
    Scans to between -threshold to threshold radians
    Returns -1 for if it loses sight of marker during correcting or timeout
    '''
    print("turnSee")
    target_marker = findTarget(targetid)
    startTime = robot.time()
    TIMEOUT = 15

    while target_marker == None:
        print("None found turnSee")
        turn(clockwise_turn)
        checkStuck()
        robot.sleep(WAIT)
        brake()
        robot.sleep(1.5*WAIT)
        target_marker = findTarget(targetid)
        print(target_marker)
        if robot.time() - startTime > TIMEOUT:
            print("turnSee timed out")
            return -1

        
    print("Correcting")
    while target_marker.position.horizontal_angle < -threshold or target_marker.position.horizontal_angle > threshold:
        target_marker = findTarget(targetid)
        if target_marker == None:
            return -1
        if target_marker.position.horizontal_angle < -3*threshold:
            turn(False, 0.2)
        if target_marker.position.horizontal_angle > 3*threshold:
            turn(True, 0.2)
        elif target_marker.position.horizontal_angle < -threshold:
            turn(False, -0.04)
        elif target_marker.position.horizontal_angle > threshold:
            turn(True, -0.04)
        print(target_marker.position.horizontal_angle)
        robot.sleep(WAIT)
        brake()
        robot.sleep(1.5*WAIT)
    print(f"Found marker, {target_marker}")
    brake()


def markerApproach(targetid, distance, threshold=0.1):
    '''
    Approaches the nearest asteroid (the one directly ahead)
    Returns -1 if loses sight of asteroid
    '''
    print("markerApproach")
    target_marker = findTarget(targetid)
    if target_marker == None:
        return -1
    notMoving = 0
    
    markerDist = target_marker.position.distance
    speed = 0.2
    waitTime = WAIT
    while markerDist > distance:
        if markerDist > 3000:
            waitTime = WAIT * 3
        elif markerDist > 1500:
            speed = 0.35
            waitTime = WAIT * 2
        else:
            speed = 0.2
        print("Driving")
        drive(speed)
        robot.sleep(waitTime)
            
        checkStuck()
        brake()
        robot.sleep(waitTime)
        turnSee(target_marker.id, False, threshold)
        target_marker = findTarget(targetid)
        if target_marker == None:
            return -1
        markerDist = target_marker.position.distance
    brake()

def spaceshipMove():
    turnSee(PORT_ID, True, 0.1)
    drive(0.2)
    robot.sleep(3.5)
    brake()
    robot.sleep(0.1)
    mtrs[0].power = -0.9
    mtrs[1].power = -0.9
    robot.sleep(2)
    turn(False, 0.5)
    robot.sleep(0.7)
    brake()
    robot.sleep(0.1)

def baseUntilUnsee(base_id):
    '''
    Approaches base
    Returns -1 if loses sight of base
    '''
    print("baseUntilUnsee")
    target_marker = findTarget(base_id)
    if target_marker == None:
        return -1
    notMoving = 0
    speed = 0.3
    driveTime = 0.8
    stopTime = driveTime * 1.5
    markerDist = 1000000
    while target_marker and len([marker for marker in robot.camera.see() if marker in BASE_IDS]) == 0:

        if markerDist > 3000:
            driveTime *= 2
            stopTime = driveTime * 1.5
        print("Driving")
        drive(speed)
        robot.sleep(driveTime)
            
        checkStuck()
        brake()
        robot.sleep(stopTime)
        target_marker = findTarget(base_id)
        if target_marker == None:
            return -1
        markerDist = target_marker.position.distance
    brake()


def microswitchDrive():
    """Drive until microswitch triggers"""
    print("microswitchDrive")
    TIMEOUT = 9
    startTime = robot.time()
    while robot.time() - startTime < TIMEOUT:
        drive()
        microswitchState = uno.pins[7].digital_read()
        print(f"Microswitch state: {microswitchState}")

        checkStuck()
        if microswitchState:
            brake()
            return
        
        robot.sleep(0.1)

def checkStuck():
    print(f"Motor currents/A: {mtrs[0].current}; {mtrs[1].current}")
    isStuck = (mtrs[0].current > UPPER_THRESHOLD_CURRENT and mtrs[1].current > UPPER_THRESHOLD_CURRENT)
    iter = 0
    while isStuck:
        print("WE ARE STUCK UPPER EXCEEEDED")
        if iter % 2:
            reverse(0.5)
        else:
            turn([True, False][randint(0,1)], 0.8)
        robot.sleep(float(randint(5,15))/10)
        isStuck = (mtrs[0].current > UPPER_THRESHOLD_CURRENT and mtrs[1].current > UPPER_THRESHOLD_CURRENT)
        iter += 1


def helpICantSee():
    """Move us into a better position for seeing"""
    print("cant see help")
    match randint(1,4):
        case 1: 
            turn([True, False][randint(0,1)], 0.4)
        case 2:
            drive(0.3)
        case 3:
            reverse()
        case 4:
            reverse()
    robot.sleep(float(randint(5,15))/10)
    brake()
    robot.sleep(WAIT)


def helpImStuck(iter):
    #Aggressively move us out of being stuck
    if iter % 3 == 2:
        reverse(0.5)
    if iter % 3 == 1:
        turn([True, False][randint(0,1)], 0.8)
    else:
        drive(0.6)
    robot.sleep(float(randint(5,15))/10)

def release():
    mech_board[0].power = -0.6
    robot.sleep(1)
    mech_board[0].power = 0
    turn(False, 0.15)
    robot.sleep(1.5*WAIT)
    reverse()
    robot.sleep(1)
    mech_board[0].power = 0.6
    robot.sleep(0.47)
    mech_board[0].power = 0
    return


def eggChecker():
    print("eggChecker")
    NEAR_ADJACENT_OPPONENT_IDS = [i for i in range(((robot.zone + 1) % 4) * 7 + 1, ((robot.zone + 2) % 4) * 7)]
    TIMEOUT = 15
    startTime = robot.time()
    # while we don't see asteroids or the far half of the adjacent opponents' bases
    while len([marker for marker in robot.camera.see() if marker.id in ASTEROID_IDS]) == 0 and \
            len([marker for marker in robot.camera.see() if marker.id in NEAR_ADJACENT_OPPONENT_IDS]) == 0:
        print("scanning for egg")
        turn(True) # the direction in which it turns alternates each time to allow for checking if the egg is in our base
        robot.sleep(2.5*WAIT)
        brake()
        robot.sleep(WAIT)
        if findTarget(EGG_ID):
            print("EGG IS IN OUR BASE!")
            return True
        if robot.time() - startTime > TIMEOUT:
            return False
    return False


def eggApproach():
    """Approaches the egg. Returns -1 if timeout"""
    print("egg approach")
    TIMEOUT = 15
    startTime = robot.time()
    while turnSee(EGG_ID, False, 0.05) == -1:
        if robot.time() - startTime > TIMEOUT:
            print("Timeout on turnSee for egg")
            return -1
    while markerApproach(EGG_ID, 700) == -1 and robot.time() - startTime < TIMEOUT:
        helpICantSee()
        if robot.time() - startTime > TIMEOUT:
            print("Timeout on turnSee for egg")
            return -1
    microswitchDrive()


def eggMover():
    """
    Moves egg to either of the two adjacent opponents' arenas.
    Returns -1 for timeout
    """
    print("eggMover")

    print("finding closest enemy marker adjacent to us")
    ADJACENT_OPPONENT_IDS = [i for i in range(((robot.zone + 1) % 4) * 7, ((robot.zone + 2) % 4) * 7)] + \
            [i for i in range(((robot.zone + 3) % 4) * 7, (robot.zone * 7 - 1) % 27)]
    chosen_opponent_marker = closestMarker(True, ADJACENT_OPPONENT_IDS)
    """opponent_markers = sorted(opponent_markers, key=lambda marker: marker.position.distance)
    chosen_opponent_marker = opponent_markers[0]"""
    
    print("turning to this marker")
    while turnSee(chosen_opponent_marker, False, 0.1) == -1:
        helpICantSee()
        chosen_opponent_marker = closestMarker(True, ADJACENT_OPPONENT_IDS)
        return
    
    print("approaching enemy marker")
    while markerApproach(chosen_opponent_marker, 800) == -1:
        helpICantSee()
        print("RESETEGGMOVER")
        eggMover() # reset
        return

    brake()
    robot.sleep(WAIT)

    release()
    
    return




def main(first=False):
    print("START")
    if first:
        direction_for_start = False
    else:
        direction_for_start = True
    asteroid = closestMarker(direction_for_start, ASTEROID_IDS)
    closest_marker_failure_count = 0
    while asteroid == None:
        helpICantSee()
        asteroid = closestMarker(direction_for_start, ASTEROID_IDS)
        closest_marker_failure_count += 1
        if closest_marker_failure_count:
            helpImStuck()
    robot.sleep(WAIT)

    if turnSee(asteroid.id, not direction_for_start, 0.05) == -1:
        main()
        return
    if markerApproach(asteroid.id, 500) == -1:
        reverse()
        robot.sleep(0.3)
        main()
        return
    
    microswitchDrive()
    robot.sleep(WAIT)
    mtrs[0].power = 0.3
    robot.sleep(0.5)
    brake()

    print("finding base")
    CHOSEN_BASE_IDS = BASE_IDS[2:-1]
    base = closestMarker(True, CHOSEN_BASE_IDS)
    failure_count = 0
    while base == None:
        if failure_count < 2:
            helpICantSee()
            base = closestMarker(True, BASE_IDS)
            failure_count += 1
        else:
            release()
            main()
    while turnSee(base.id, True, 0.1) == -1:
        base = closestMarker(True, CHOSEN_BASE_IDS)
        while base == None:
            helpICantSee()
            base = closestMarker(True, CHOSEN_BASE_IDS)
    while baseUntilUnsee(base.id) == -1:
    #while markerApproach(base.id, 800, 0.2) == -1:
        base = closestMarker(True, CHOSEN_BASE_IDS)
        while base == None:
            if failure_count < 2:
                helpICantSee()
                base = closestMarker(True, BASE_IDS)
                failure_count += 1
            else:
                release()
                ASTEROID_IDS.remove(asteroid.id)
                main()
    
    brake()
    robot.sleep(WAIT)

    release()

    ASTEROID_IDS.remove(asteroid.id)
    iters = 0
    if eggChecker():
        if eggApproach() == -1 and iters < 1:
            helpICantSee()
            eggApproach() # get it next iteration
            iters += 1 
        if eggMover() == -1:
            main() # get it next iteration

    global iteration_no
    iteration_no += 1

print(robot.zone)

spaceshipMove()
main(True)

while True:
    try:
        main()
    except:
        print("ERROR" + '-'*100)
        main()