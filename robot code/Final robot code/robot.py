# Draft started 24/2/24

from sr.robot3 import *

robot = Robot()
motors = robot.motor_board.motors
uno = robot.arduino

CPR = 2 * math.pi / (4 * 11)
WHEEL_DIAMETER = 80
MARKERSDICT = {
    "boundary": [i for i in range(28)],
    "asteroid": [i for i in range(150, 200)],
    "egg": [110],
    "port": [i for i in range(120, 124)],
    "starboard": [i for i in range(125, 128)]
}


def brake():
    '''Stop moving robot.'''
    motors[0].power = 0
    motors[1].power = 0

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
    '''Pick up and lift an asteroid/egg in front of the robot.'''
    pass

def mechanismRelease():
    '''Release an asteroid, and lower the arms.'''
    pass

def getEncoderDistance():
    encoderCount = int(uno.command("v"))
    distance = (encoderCount / CPR) * math.pi * WHEEL_DIAMETER
    print(f"Count: {encoderCount},\t Distance: {distance}mm")
    return distance

def approachAsteroid(targetMarker):
    '''Move towards an asteroid, and pick it up.'''
    marker = findMarker(targetMarker)
    while marker.position.horizontal_angle > 0.1:
        motors[0].power = 0.2
        motors[1].power = -0.2
    while marker.position.horizontal_angle < 0.1:
        motors[0].power = -0.2
        motors[1].power = 0.2
    brake()
    robot.sleep(0.1)
    marker = findMarker(targetMarker)
    while marker.position.distance > 30:
        motors[0].power = 0.4
        motors[1].power = 0.4

def approachBase():
    pass

def main():
    approachAsteroid()
    mechanismGrab()
    approachBase()
    mechanismRelease()
    
    # check if egg in base

    
