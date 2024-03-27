from sr.robot3 import *
robot = Robot()

mts = robot.motor_board.motors

while True:
    markers = robot.camera.see()
    mts[0].power = 0
    mts[1].power = 0

    if markers:
        while not -0.05 < markers[0].position.horizontal_angle < 0.05:
            markers = robot.camera.see()
            mts[0].power = 0.2
            mts[1].power = -0.2
        mts[0].power = 0.5
        mts[1].power = 0.5

        if markers[0].distance < 50:
            mts[0].power = 0
            mts[1].power = 0
            break
                
