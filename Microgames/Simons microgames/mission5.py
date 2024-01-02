from sr.robot3 import *
robot = Robot()
#5 errors

def spin(duration, speed):
    # make robot spin
    robot.motor_board.motors[0].power = speed
    robot.motor_board.motors[1].power = -speed
    #fixed minor spelling mistake
    robot.sleep(duration)
    robot.motor_board.motors[0].power = 0
    #set channel to 1
    robot.motor_board.motors[1].power = 0

def look_for_any_marker():
    markers = robot.camera.see()
    if len(markers) > 0:
        print("Found a marker!")
        return markers[0]

# Main code, tries to face a marker
marker = None
duration = 0.01
#removed indent
speed = 0.1
#added colon
while True:
    marker = look_for_any_marker()
    if marker is not None:
        #removed string around 0
        if marker.position.horizontal_angle > 0:
            spin(duration, speed)
        else:
            spin(duration, -speed)