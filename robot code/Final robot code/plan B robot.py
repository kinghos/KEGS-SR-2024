"""
    Current robot code for plan B (no mechanism)

"""

from sr.robot3 import *
from math import pi
from random import randint

robot = Robot()
mtrs = robot.motor_boards["SR0UK1L"].motors
mech_board = robot.motor_boards["SR0KJ15"].motors
uno = robot.arduino

CPR = 2 * pi * 1000/ (4*11 * 0.229) # Magic functioning as of 19.03.24
WHEEL_DIAMETER = 80
ASTEROID_IDS = [i for i in range(150, 200)]
BASE_IDS = [i for i in range(8)]

TURNSPEED = 0.18
DRIVESPEED = 0.3
WAIT = 0.25

TIMEOUT = 40

def brake():
    '''Sets both motors' power to 0.'''
    mtrs[0].power = 0
    mtrs[1].power = 0

'''Speed level of 0 means default speed, and levels above that are added'''
def turn(clockwise=True, speed_level=0):
    if clockwise: 
        mtrs[0].power = (TURNSPEED+speed_level)
        mtrs[1].power = -(2*TURNSPEED+speed_level)
    else:
        mtrs[0].power = -(2*TURNSPEED+speed_level)
        mtrs[1].power = (TURNSPEED+speed_level)

def drive(speed_level=0):
    mtrs[0].power = DRIVESPEED+speed_level
    mtrs[1].power = DRIVESPEED+speed_level

def reverse():
    mtrs[0].power = -DRIVESPEED
    mtrs[1].power = -DRIVESPEED


def getEncoderCount(motor):
    if motor == "left":
        command = "e"
    else:
        command = "f"
    while True:
        robot.sleep(0.05)
        strEncoderCount = uno.command(command)
        if strEncoderCount: # Checks for non-empty string
            encoderCount = float(strEncoderCount)
            return encoderCount
    

def calculateDistance(encoderCount, motor=None):
    distance = (encoderCount / CPR) * pi * WHEEL_DIAMETER # Distance in mm
    return distance


def findTarget(targetid):
    '''Identify a marker based on its ID. Return the marker object if found, else return None.'''
    markers = robot.camera.see()
    for marker in markers:
        if marker.id == targetid:
            return marker
    print(f'look couldnt find {targetid}')
    return None


def closestMarker(clockwise_turn, type):
    '''Returns None if not found / timeout'''
    markers = []
    print("closestMarker")
    startTime = robot.time()

    while len(markers) == 0 and robot.time() - startTime < TIMEOUT:
        markers = [marker for marker in robot.camera.see() if marker.id in type]
        turn(clockwise_turn)
        robot.sleep(2*WAIT)
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
        if target_marker.position.horizontal_angle < -3*threshold:
            turn(False, 0.2)
        if target_marker.position.horizontal_angle > 3*threshold:
            turn(True, 0.2)
        elif target_marker.position.horizontal_angle < -threshold:
            turn(False)
        elif target_marker.position.horizontal_angle > threshold:
            turn(True)
        print(target_marker.position.horizontal_angle)
        robot.sleep(0.9*WAIT)
        brake()
        robot.sleep(WAIT)
    print(f"Found marker, {target_marker}")
    brake()


def markerApproach(targetid, distance, threshold=0.1):
    print("APPROACH")
    '''Approaches the nearest asteroid (the one directly ahead)'''
    target_marker = findTarget(targetid)
    if target_marker == None:
        return -1
    
    prevDistance = calculateDistance(getEncoderCount("left"))
    while target_marker.position.distance > distance:
        target_marker = findTarget(targetid)
        if target_marker == None:
            return -1
        if target_marker.position.distance <= distance:
            break
        print("driving")
        drive()
        robot.sleep(WAIT)
        print(f"Motor currents/A: {mtrs[0].current}; {mtrs[1].current}")
        currDistance = calculateDistance(getEncoderCount("left"))
        if currDistance - prevDistance < 20: #if we haven't moved more than 20mm since last repetition of while loop
            print("We may be stuck...")
            helpICantSee() #FIXME: change to helpImStuck later
        brake()
        robot.sleep(WAIT)
        turnSee(target_marker.id, False, threshold)
        prevDistance = currDistance
    brake()

def encoderDrive(distance):
    print("encoderdrive")
    startTime = robot.time()
    startDistance = calculateDistance(getEncoderCount("left"))
    print("start: ", startDistance)
    while robot.time() - startTime < TIMEOUT:
        drive()
        encoderCount = getEncoderCount("left")
        encoderDistance = calculateDistance(encoderCount, "left") - startDistance
        print(f"Encoder distance: {encoderDistance}")
        print(f"Count: {encoderCount}\t Distance: {encoderDistance}")
        if encoderDistance >= (distance):
            brake()
            return
        robot.sleep(0.1)


def helpICantSee():
    match randint(0,2):
        case 0:
            reverse()
        case 1: 
            turn(True, 0.5)
        case 2:
            drive(0.5)
    robot.sleep(2)
    brake()
    robot.sleep(WAIT)

def helpImStuck():
    return

def release():
    mech_board[0].power = -0.6
    robot.sleep(0.6)
    mech_board[0].power = 0
    reverse()
    robot.sleep(1)
    mech_board[0].power = 0.6
    robot.sleep(0.6)
    mech_board[0].power = 0
    return

def eggChecker():
    if findTarget(110) != None and any([findTarget(base_id) for base_id in BASE_IDS]):
        print("I see the egg and a base id at the same time!!!!!")
        turnSee(110, False, 0.05)
        markerApproach(110, 700)
        encoderDrive(700)
        print("I have got the egg") #FIXME: ADD EGGMOVING CODE TO MOVE TO ANOTHER BASE
        print("eggchecker returning")

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
    encoderDrive(700)
    robot.sleep(WAIT)
    mtrs[0].power = 0.3
    robot.sleep(0.5)
    brake()

    base = closestMarker(True, BASE_IDS)
    while base == None:
        helpICantSee()
        asteroid = closestMarker(True, BASE_IDS)
    if turnSee(base.id, False, 0.2) == -1:
        main()
        return
    while markerApproach(base.id, 1500, 0.3) == -1:
        markerApproach(base.id, 1500, 0.3)
    drive()
    robot.sleep(2)
    brake()
    robot.sleep(WAIT)

    release()

    reverse()
    robot.sleep(2)

while True:
    main()
