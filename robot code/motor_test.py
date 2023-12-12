from sr.robot3 import *
robot = Robot()

mb = robot.motor_board.motors

def brake():
    mb[0].power = 0
    mb[1].power = 0


mb.motors[0].power = 0.4
mb.motors[1].power = 0.4

robot.sleep(5)
brake()
robot.sleep(1)

mb.motors[0].power = -0.4
mb.motors[1].power = -0.4

robot.sleep(5)
brake()
robot.sleep(1)

mb.motors[0].power = 0.4
mb.motors[1].power = -0.4

robot.sleep(1)