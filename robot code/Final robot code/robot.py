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
    '''Identify a marker based on its ID. Return the marker object if found, else return None.'''
    markers = robot.camera.see()
    for marker in markers:
        if marker.id == targetMarker:
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
    mechanismMotors[0].power = 0.5
    robot.sleep(1.2)
    mechanismMotors[0].power = 0
    

def mechanismRelease():
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
    startTime = robot.time()
    while robot.time() - startTime < TIMEOUT:
        markers = robot.camera.see()
        for marker in markers:
            if marker.id in MARKERSDICT["asteroid"]:
                brake()
                print(f"Found closest asteroid: {marker.id}")
                return marker
        turn(0.3)
    brake()
    print("Couldn't find any asteroids")
    return None
    

def approachAsteroid(targetMarker): ## TODO Add encoder based routing
    '''Move towards an asteroid, and pick it up.'''
    while marker.position.horizontal_angle > 0.1:
        marker = findMarker(targetMarker) # FIXME Add checks for None 
        turn(0.2)
    while marker.position.horizontal_angle < 0.1:
        marker = findMarker(targetMarker) # FIXME Add checks for None 
        turn(-0.2)
    brake()
    robot.sleep(0.05)
    marker = findMarker(targetMarker)
    while marker.position.distance > 30:
        marker = findMarker(targetMarker)
        drive(0.4)


def approachBase():
    markers = []
    startTime = robot.time()



def main():
    approachAsteroid()
    mechanismGrab()
    approachBase()
    mechanismRelease()
    
    # check if egg in base

    
