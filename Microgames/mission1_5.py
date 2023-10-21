# NB: Don't actually know if these are the bugs, just assuming they are (would actually need to test in school to check)

from sr.robot3 import *

robot = Robot()

def spin(duration, speed):
    # make robot spin
    robot.motor_board.motors[0].power = speed
    robot.motor_board.motors[1].power = -speed
    robot.sleep(duration) # Bug 1
    robot.motor_board.motors[0].power = 0
    robot.motor_board.motors[1].power = 0 # Bug 2

def look_for_any_marker():
    markers = robot.camera.see()
    if len(markers) > 0:
        print("Found a marker!")
        return markers[0]

# Main code, tries to face a marker
marker = None
duration = 0.01
speed = 0.1 # Bug 3
while True: # Bug 4
    marker = look_for_any_marker()
    if marker is not None:
        if marker.position.horizontal_angle > 0: # Bug 5
            spin(duration, speed)
        else:
            spin(duration, -speed)