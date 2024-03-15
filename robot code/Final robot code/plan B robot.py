"""
    Current robot code for plan B (no mechanism)

"""

from sr.robot3 import *
from math import pi

robot = Robot()
mtrs = robot.motor_boards["SR0UK1L"].motors
uno = robot.arduino

CPR = 2 * pi / (4 * 11)
WHEEL_DIAMETER = 80
ASTEROID_IDS = [i for i in range(150, 200)]
BASE_IDS = [i for i in range(8)]

TURNSPEED = 0.22
DRIVESPEED = 0.3
WAIT = 0.4

TIMEOUT = 10

def brake():
    '''Sets both motors' power to 0.'''
    mtrs[0].power = 0
    mtrs[1].power = 0

def turn(dir=True): #fix this - is dir clockwise or anticlockwise?
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
    print(f"Motor: {motor:<4}\t Count: {encoderCount:<10}\t Distance: {distance/1000:<10.4f}m")
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