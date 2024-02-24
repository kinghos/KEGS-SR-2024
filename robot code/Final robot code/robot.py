# Draft started 24/2/24

from sr.robot3 import *

robot = Robot()
motors = robot.motor_board.motors
uno = robot.arduino

CPR = 2 * math.pi / (4 * 11)
WHEEL_DIAMETER = 80

def brake():
    motors[0].power = 0
    motors[1].power = 0

def findMarker(marker):
    pass

def mechanismGrab():
    pass

def mechanismRelease():
    pass

def approachAsteroid(marker):
    findMarker(marker)

def approachBase():
    pass

def main():
    approachAsteroid()
    mechanismGrab()
    approachBase()
    mechanismRelease()
    
    # check if egg in base

    
