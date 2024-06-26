# Draft started 24/2/24

from sr.robot3 import *
from math import pi

robot = Robot()
driveMotors = robot.motor_board['srXXXX'].motors # Needs serial no.
mechanismMotors = robot.motor_board['srXXXX'].motors # Needs serial no.
uno = robot.arduino

CPR = 2 * pi / (4 * 11)
WHEEL_DIAMETER = 80
MARKERSDICT = {
    "planet 0": [i for i in range(7)],
    "planet 1": [i for i in range(7, 14)],
    "planet 2": [i for i in range(14, 21)],
    "planet 3": [i for i in range(21, 28)],
    "asteroid": [i for i in range(150, 200)],
    "egg": [110],
    "port": [i for i in range(120, 124)],
    "starboard": [i for i in range(125, 128)]
}
TIMEOUT = 10 # seconds before a vision function times out
DRIVESPEED = 0.4
TURNSPEED = 0.25
DISTANCETHRESHOLD = 50 # mm
ANGLETHRESHOLD = 0.1 # radians

def brake():
    '''Stop moving robot.'''
    driveMotors[0].power = 0
    driveMotors[1].power = 0


def drive(speed):
    '''Drive robot at a constant speed.'''
    driveMotors[0].power = speed
    driveMotors[1].power = speed

def turn(speed):
    '''Turn robot at a constant speed'''
    driveMotors[0].power = speed
    driveMotors[1].power = -speed


def findMarker(targetMarker):
    brake()
    robot.sleep(0.25)
    '''Identify a marker based on its ID. Return the marker object if found, else return None.'''
    markers = robot.camera.see()
    for marker in markers:
        if marker.id == targetMarker:
            print(f"Found {targetMarker}")
            return marker
    print(f"Couldn't find {targetMarker}")
    return None


def findMarkerType(mType):
    '''Identify a marker based on its type. Return the marker object if found, else return None.'''
    markers = robot.camera.see()
    for marker in markers:
        if marker.id in MARKERSDICT[mType]:
            return marker
    print(f"Couldn't find {mType}")
    return None


def mechanismGrab():
    '''Grab an asteroid'''
    print("Grabbing asteroid")
    mechanismMotors[0].power = 0.5
    robot.sleep(1.2)
    mechanismMotors[0].power = 0
    

def mechanismRelease():
    print("Releasing asteroid")
    '''Release an asteroid'''
    mechanismMotors[0].power = -0.5
    robot.sleep(1.2)
    mechanismMotors[0].power = 0


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


def lookForClosestAsteroid():
    markers = []
    asteroids = []
    print("Looking for closest asteroid")
    startTime = robot.time()

    while robot.time() - startTime < TIMEOUT:
        robot.sleep(0.25)
        brake()
        robot.sleep(0.1)

        markers = robot.camera.see()
        for marker in markers:
            if marker.id in MARKERSDICT["asteroid"]:
                print(f"Found asteroid: {marker.id}")
                asteroids.append(marker)
        turn(TURNSPEED)

    brake()
    closestAsteroid = None
    minimum = float("inf")
    for marker in asteroids:
        if marker.position.distance < minimum:
            mimimum = marker.position.distance
            closestAsteroid = marker
    print("Closest asteroid: ", closestAsteroid.id)
    return closestAsteroid
            
    print("Couldn't find any asteroids")
    return None
    

def approachAsteroid(targetMarker): ## TODO Add encoder based routing
    '''Move towards an asteroid until it is within 30mm of the robot.'''
    marker = findMarker(targetMarker.id)
    while marker.position.distance > DISTANCETHRESHOLD:
        marker = findMarker(targetMarker.id)
        print("Distance: ", marker.position.distance)
        drive(DRIVESPEED)

def turnSee(targetid):
    '''
    Scans the surroundings for asteroids, going clockwise.
    Scans to between -0.08 to 0.08 radians
    '''
    print("Looking for marker", targetid)
    target_marker = findMarker(targetid)
    while target_marker == None:
        print("Marker not found, turning to find it")
        turn(TURNSPEED)
        robot.sleep(0.25)
        brake()
        robot.sleep(0.1)
        target_marker = findMarker(targetid)
        print("Looking for marker", targetid)
    
    print("Correcting angle")
    while target_marker.position.horizontal_angle < -ANGLETHRESHOLD or target_marker.position.horizontal_angle > ANGLETHRESHOLD:
        target_marker = findMarker(targetid)
        if target_marker == None:
            return -1
        if target_marker.position.horizontal_angle < -ANGLETHRESHOLD:
            turn(TURNSPEED)
        if target_marker.position.horizontal_angle > ANGLETHRESHOLD:
            turn(-TURNSPEED)
        print(f"Horizontal angle: {target_marker.position.horizontal_angle}")
        robot.sleep(0.3)
        brake()
        robot.sleep(0.1)
    print(f"Found marker, {target_marker}")
    brake()


def approachBase():
    '''Approach the base zone to deposit asteroids'''
    markers = []
    startTime = robot.time()
    found = False
    targetMarker = 0
    while robot.time() - startTime < TIMEOUT and not found:
        brake()
        robot.sleep(0.25)
        markers = robot.camera.see()
        for marker in markers:
            if marker.id in MARKERSDICT["planet " + str(robot.zone)]:
                brake()
                print(f"Found base: {marker.id}")
                found == True
                targetMarker = marker.id
        turn(TURNSPEED)

    brake()
    if not found:
        print("Couldn't find base")
        return None
    else:
        while marker.position.horizontal_angle > 0.1:
            marker = findMarker(targetMarker.id) # FIXME Add checks for None 
            print("Horizontal angle: ", marker.position.horizontal_angle)
            turn(TURNSPEED)
        while marker.position.horizontal_angle < 0.1:
            marker = findMarker(targetMarker.id) # FIXME Add checks for None 
            print("Horizontal angle: ", marker.position.horizontal_angle)
            turn(-TURNSPEED)
        brake()
        print("Aligned with base")
        robot.sleep(0.05)
        marker = findMarker(targetMarker) # FIXME Add checks for None
        while marker.position.distance > 200:
            marker = findMarker(targetMarker.id)
            print("Distance: ", marker.position.distance)
            drive(DRIVESPEED)
        return True

def main():
    while True:
        marker = lookForClosestAsteroid()
        turnSee(marker.id)
        approachAsteroid(marker)
        drive(DRIVESPEED)
        robot.sleep(1.2)
        brake()
        driveMotors[0].power = DRIVESPEED
        robot.sleep(1)
        brake()
        approachBase()
    
main()