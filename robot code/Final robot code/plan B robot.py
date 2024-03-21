"""
    Current robot code for plan B+
    Last tested: 20.03.24 afterschool
    Untested stuff:
     - All contingencies
     - Egg functions
     - Check how motor current behaves - would help if the robot is stuck on raised platform
    TODO:
     - Add checking for if we have done a full revolution without seeing target marker for closestMarker and turnSee
     - Add closestMarker stuff from simulation (turn to see the opposite left and right markers before making the choice as to which asteroid is closest)
     - FIXME: encoder & microswitch trouble
"""

from sr.robot3 import *
from math import pi
from random import randint

robot = Robot()
mtrs = robot.motor_boards["SR0UK1L"].motors # driving motors
mech_board = robot.motor_boards["SR0KJ15"].motors
uno = robot.arduino
robot.arduino.pins[7].mode = INPUT_PULLUP

iteration_no = 0 # number of iterations of main while loop

CPR = 2 * pi * 1000/ (4*11 * 0.229) # Magic functioning as of 19.03.24
WHEEL_DIAMETER = 80
ASTEROID_IDS = [i for i in range(150, 200)]
BASE_IDS = [i for i in range(robot.zone * 7, (robot.zone + 1) * 7)] # To change zone click settings on robot.lan (defaults to 0)
NUMBER_OF_WALL_MARKERS = 28
EGG_ID = 110
PORT_ID = robot.zone + 120
STARBOARD_ID = robot.zone + 125

TURNSPEED = 0.15
DRIVESPEED = 0.25
WAIT = 0.2

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
    mtrs[1].power = (DRIVESPEED+speed_level) % 1

def reverse(speed_level=0):
    '''Speed level: defaults to 0, added to the default turnspeed'''
    mtrs[0].power = -(DRIVESPEED+speed_level)
    mtrs[1].power = -(DRIVESPEED+speed_level)


def getEncoderCount(motor): #FIXME
    if motor == "left":
        command = "e"
    else:
        command = "f"
    while True:
        robot.sleep(0.05)
        sensorInfo = uno.command(command)
        strEncoderCount = sensorInfo[0]
        try:
            if strEncoderCount: # Checks for non-empty string
                encoderCount = float(strEncoderCount)
                return encoderCount
        except ValueError:
            print("Got a weird letter", strEncoderCount)
    

def calculateDistance(encoderCount, motor=None):
    distance = (encoderCount / CPR) * pi * WHEEL_DIAMETER # Distance in mm
    return distance

def microswitch(): #FIXME
    print("Microswitch:", not robot.arduino.pins[7].digital_read())
    return not robot.arduino.pins[7].digital_read()

def findTarget(targetid):
    '''Identify a marker based on its ID. Return the marker object if found, else return None.'''
    markers = robot.camera.see()
    for marker in markers:
        if marker.id == targetid:
            return marker
    print(f"findTarget couldn't find {targetid}")
    return None


def closestMarker(clockwise_turn, type):
    '''
    Returns the first marker it sees whilst turning
    Returns None if not found / timeout
    '''
    print("closestMarker")
    markers = []
    startTime = robot.time()
    TIMEOUT = 25

    while len(markers) == 0 and robot.time() - startTime < TIMEOUT:
        markers = [marker for marker in robot.camera.see() if marker.id in type]
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
    TIMEOUT = 12

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
        if target_marker.position.horizontal_angle < -2.5*threshold:
            turn(False, 0.2)
        if target_marker.position.horizontal_angle > 2.5*threshold:
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
    
    prevDistance = calculateDistance(getEncoderCount("left"))
    notMoving = 0
    while target_marker.position.distance > distance:
        print("Driving")
        drive(0.2)
        robot.sleep(WAIT)
        print(f"Motor currents/A: {mtrs[0].current}; {mtrs[1].current}")
        currDistance = calculateDistance(getEncoderCount("left"))
            
        if currDistance - prevDistance < 20:
            notMoving += 1
            if notMoving > 4:
                print("We are stuck against a wall, but wheels still touch the ground")
                helpICantSee()
        else:
            notMoving = 0

        #elif motorcurrents dropped v rapidly:
        #    print("Motors are in the air!")
        #    helpImStuck()
        brake()
        robot.sleep(WAIT)
        turnSee(target_marker.id, False, threshold)
        prevDistance = currDistance
        target_marker = findTarget(targetid)
        if target_marker == None:
            return -1
    brake()



def encoderMicroswitchDrive(distance, useMicroswitch=False):
    """Drive a set distance using encoders"""
    print("encoderDrive")
    TIMEOUT = 5
    startTime = robot.time()
    startDistance = calculateDistance(getEncoderCount("left")) #FIXME: adjust for microswitch
    prevDistance = 0
    print("start: ", startDistance)
    prevMicroswitchState = 0
    notMoving = 0
    while robot.time() - startTime < TIMEOUT or encoderDistance > 2*distance:
        drive()
        encoderCount = getEncoderCount("left") #FIXME: adjust for microswitch
        encoderDistance = calculateDistance(encoderCount, "left") - startDistance #FIXME: adjust for microswitch
        print(f"Encoder Count: {encoderCount}\t Distance: {encoderDistance}")

        if useMicroswitch:
            if encoderDistance >= 0.7*distance and (prevMicroswitchState > 3): # if microswitch has been pressed for 3 consecutive iterations
                print("Reached distance AND microswitch pressed")
                brake()
                return
        else:
            if encoderDistance >= (distance):
                brake()
                return
            
        if encoderDistance - prevDistance < 20:
            notMoving += 1
            if notMoving > 4:
                print("We are stuck against a wall, but wheels still touch the ground")
                helpICantSee()
        else:
            notMoving = 0

        robot.sleep(WAIT)
        prevDistance = encoderDistance
        if microswitch():
            prevMicroswitchState += 1
        else:
            prevMicroswitchState = 0



def helpICantSee():
    """Move us into a better position for seeing"""
    print("cant see help")
    match randint(0,2):
        case 0:
            reverse()
        case 1: 
            turn(True, 0.15)
        case 2:
            drive(0.4)
    robot.sleep(1)
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
    robot.sleep(0.6)
    mech_board[0].power = 0
    turn(False)
    robot.sleep(1.5*WAIT)
    reverse()
    robot.sleep(2)
    mech_board[0].power = 0.6
    robot.sleep(0.47)
    mech_board[0].power = 0
    return


def eggChecker():
    print("eggChecker")
    NEAR_ADJACENT_OPPONENT_IDS = [i for i in range(((robot.zone + 1) % 4) * 7, ((robot.zone + 1) % 4) * 7 + 3)] + \
            [i for i in range(((robot.zone + 3) % 4) * 7, ((robot.zone + 3) % 4) * 7 + 3)]
    # while we don't see asteroids or the far half of the adjacent opponents' bases
    while len([marker for marker in robot.camera.see() if marker.id in ASTEROID_IDS]) == 0 and \
            len([marker for marker in robot.camera.see() if marker.id in NEAR_ADJACENT_OPPONENT_IDS]) == 0:
        print("scanning for egg")
        turn(bool(iteration_no % 2), 0.4) # the direction in which it turns alternates each time to allow for checking if the egg is in our base
        robot.sleep(WAIT)
        brake()
        robot.sleep(WAIT)
        if findTarget(EGG_ID):
            print("EGG IS IN OUR BASE!")
            return True
    return False


def eggApproach():
    """Approaches the egg. Returns -1 if timeout"""
    TIMEOUT = 10
    startTime = robot.time()
    while turnSee(EGG_ID, not bool(iteration_no % 2), 0.05) == -1:
        helpICantSee()
        if robot.time() - startTime < TIMEOUT:
            print("Timeout on turnSee for egg")
            return -1
    while markerApproach(EGG_ID, 700) == -1 and robot.time() - startTime < TIMEOUT:
        helpICantSee()
        if robot.time() - startTime < TIMEOUT:
            print("Timeout on turnSee for egg")
            return -1
    encoderMicroswitchDrive(700)


def eggMover():
    """
    Moves egg to either of the two adjacent opponents' arenas.
    Returns -1 for timeout
    """
    TIMEOUT = 20
    startTime = robot.time()
    while len(seen_opponent_markers) > 0:
        ADJACENT_OPPONENT_IDS = [i for i in range(((robot.zone + 1) % 4) * 7, ((robot.zone + 2) % 4) * 7)] + \
            [i for i in range(((robot.zone + 3) % 4) * 7, robot.zone * 7)]
        seen_opponent_markers = [marker for marker in robot.camera.see() if marker.id in ADJACENT_OPPONENT_IDS]
        turn()
        robot.sleep(WAIT)
        brake()
        robot.sleep(WAIT)
        if robot.time() - startTime < TIMEOUT:
            return -1

    opponent_markers = sorted(seen_opponent_markers, key=lambda marker: marker.distance)
    chosen_opponent_marker = opponent_markers[0]
    
    while turnSee(chosen_opponent_marker) == -1:
        seen_opponent_markers = [marker for marker in robot.camera.see() if marker.id in ADJACENT_OPPONENT_IDS]
        while len(seen_opponent_markers) == 0:
            helpICantSee()
            seen_opponent_markers = [marker for marker in robot.camera.see() if marker.id in ADJACENT_OPPONENT_IDS]
            if robot.time() - startTime < TIMEOUT:
                return -1
        opponent_markers = sorted(seen_opponent_markers, key=lambda marker: marker.distance)
        chosen_opponent_marker = opponent_markers[0]
        if robot.time() - startTime < TIMEOUT:
            return -1
    
    while markerApproach(chosen_opponent_marker) == -1:
        seen_opponent_markers = [marker for marker in robot.camera.see() if marker.id in ADJACENT_OPPONENT_IDS]
        while len(seen_opponent_markers) == 0:
            helpICantSee()
            seen_opponent_markers = [marker for marker in robot.camera.see() if marker.id in ADJACENT_OPPONENT_IDS]
            if robot.time() - startTime < TIMEOUT:
                return -1
        opponent_markers = sorted(seen_opponent_markers, key=lambda marker: marker.distance)
        chosen_opponent_marker = opponent_markers[0]
        if robot.time() - startTime < TIMEOUT:
            return -1

    drive()
    robot.sleep(3)
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
    if markerApproach(asteroid.id, 700) == -1:
        main()
        return
    
    #encoderDrive(700)
    encoderMicroswitchDrive(700)
    robot.sleep(WAIT)
    mtrs[0].power = 0.3
    robot.sleep(0.5)
    brake()

    base = closestMarker(True, BASE_IDS)
    while base == None:
        helpICantSee()
        base = closestMarker(True, BASE_IDS)
    while turnSee(base.id, False, 0.2) == -1:
        helpICantSee()
        base = closestMarker(True, BASE_IDS)
    while markerApproach(base.id, 1500, 0.3) == -1:
        helpICantSee()
        base = closestMarker(True, BASE_IDS)
    drive()
    robot.sleep(3)
    brake()
    robot.sleep(WAIT)

    # Everything below here needs to be tested again
    release()

    if eggChecker():
        if eggApproach() == -1:
            main() # get it next iteration
        if eggMover() == -1:
            main() # get it next iteration

    ASTEROID_IDS.remove(asteroid.id)
    global iteration_no
    iteration_no += 1



print(robot.zone)
while True:
    main()
