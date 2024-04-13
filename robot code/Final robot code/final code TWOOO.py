"""
    Current robot code for plan B+, with microswitch
    Last tested: 27.03.24
"""

from sr.robot3 import *
from math import pi
from random import randint

robot = Robot()
mtrs = robot.motor_boards["SR0UK1L"].motors # driving motors
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


def microswitch():
    while True:
        robot.sleep(0.05)
        sensorInfo = uno.command("e")
        if sensorInfo:
            print(sensorInfo)
            microswitchState = bool(int(sensorInfo.split(",")[1]))
            return microswitchState


def findTarget(targetid):
    '''Identify a marker based on its ID. Return the marker object if found, else return None.'''
    markers = robot.camera.see()
    for marker in markers:
        if marker.id == targetid:
            return marker
    print(f"findTarget couldn't find {targetid}")
    return None


"""
def closestAsteroid(clockwise_turn):
    '''
    Returns the first marker it sees whilst turning
    Returns None if not found / timeout
    '''
    print("closestMarker")
    markers = []
    markerType = ASTEROID_IDS
    startTime = robot.time()
    TIMEOUT = 25
    closest = None

    # while len(markers) == 0 and robot.time() - startTime < TIMEOUT:
    #     markers = [marker for marker in robot.camera.see() if marker.id in markerType]
    #     turn(clockwise_turn)
    #     robot.sleep(2.5*WAIT)
    #     brake()
    #     robot.sleep(WAIT)
    
    for i in range(4):
        markers = [marker for marker in robot.camera.see() if marker.id in markerType]
        if markers:
            for marker in markers:
                if closest == None:
                    closest = marker
                if marker.position.distance < closest.position.distance:
                    closest = marker
        turn(clockwise_turn)
        robot.sleep(2.5*WAIT)
        brake()
        robot.sleep(WAIT)

    print(closest)
    brake()
    return closest
"""


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
        turn(clockwise_turn)
        robot.sleep(2.5*WAIT)
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
        robot.sleep(WAIT)
        brake()
        robot.sleep(WAIT)
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
        robot.sleep(WAIT)
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
    while target_marker.position.distance > distance:
        print("Driving")
        drive(0.2)
        robot.sleep(WAIT)
        print(f"Motor currents/A: {mtrs[0].current}; {mtrs[1].current}")
            

        #elif motorcurrents dropped v rapidly:
        #    print("Motors are in the air!")
        #    helpImStuck()
        brake()
        robot.sleep(WAIT)
        turnSee(target_marker.id, False, threshold)
        target_marker = findTarget(targetid)
        if target_marker == None:
            return -1
    brake()


def encoderDrive():
    """Drive a set distance using encoders AND MICROSWITCH"""
    print("encoderDrive")
    TIMEOUT = 9
    startTime = robot.time()
    prevDistance = 0
    notMoving = 0
    while robot.time() - startTime < TIMEOUT:
        drive()
        microswitchState = uno.pins[7].digital_read()
        print(f"Microswitch state: {microswitchState}")

        if microswitchState:
            brake()
            return
        
        robot.sleep(0.1)



def helpICantSee():
    """Move us into a better position for seeing"""
    print("cant see help")
    match randint(1,4):
        case 1: 
            turn(True, 0.4)
        case 2:
            drive(0.26)
        case 3:
            reverse()
        case 4:
            reverse()
    robot.sleep(0.8)
    brake()
    robot.sleep(WAIT)


def helpImStuck():
    """Aggressively turn every motor we have randomly"""
    print("stuck")
    match randint(0,4):
        case 0:
            reverse(1)
        case 1: 
            drive(1)
        case 2:
            turn(True, 1)
        case 3:
            mech_board[0].power = 1
        case 4:
            mech_board[0].power = -1
    robot.sleep(1)
    brake()
    mech_board[0].power = 0
    robot.sleep(WAIT)


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
    encoderDrive()


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




def main():
    print("START")

    asteroid = closestMarker(True, ASTEROID_IDS)
    while asteroid == None:
        helpICantSee()
        asteroid = closestMarker(True, ASTEROID_IDS)
    robot.sleep(WAIT)

    if turnSee(asteroid.id, False, 0.05) == -1:
        main()
        return
    if markerApproach(asteroid.id, 500) == -1:
        main()
        return
    
    encoderDrive()
    robot.sleep(WAIT)
    mtrs[0].power = 0.3
    robot.sleep(0.5)
    brake()

    print("finding base")
    CHOSEN_BASE_IDS = BASE_IDS[2:-1]
    base = closestMarker(True, CHOSEN_BASE_IDS)
    while base == None:
        if failure_count < 2:
            helpICantSee()
            base = closestMarker(True, BASE_IDS)
            failure_count += 1
        else:
            release()
            main()
    while turnSee(base.id, True, 0.1) == -1:
        helpICantSee()
        base = closestMarker(True, CHOSEN_BASE_IDS)
        while base == None:
            helpICantSee()
            base = closestMarker(True, CHOSEN_BASE_IDS)
    while markerApproach(base.id, 750, 0.2) == -1:
        helpICantSee()
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
    
    # startTime = robot.time()
    # TIMEOUT = 10

    # while robot.time() - startTime > TIMEOUT:
    #     markers = robot.camera.see()
    #     base_markers = set()
    #     for i in markers:
    #         if i.id in BASE_IDS:
    #             base_markers.add(i.id)
    #             markerApproach(i.id)


    brake()
    robot.sleep(WAIT)

    # Everything below here needs to be tested again
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
while True:
    try:
        main()
    except:
        main()