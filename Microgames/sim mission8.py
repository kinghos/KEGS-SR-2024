from sr.robot3 import *
robot = Robot()


print('moving -0.4 power')
robot.motor_board.motors[0].power = -0.4
robot.motor_board.motors[1].power = -0.4
robot.sleep(0.01)

while True:
    robot.arduino.pins[2].mode = INPUT
    hurt_bum = robot.arduino.pins[2].digital_read()
    robot.sleep(0.01)
    if hurt_bum == True:
        print('ow')
        robot.motor_board.motors[0].power = 0
        robot.motor_board.motors[1].power = 0
        robot.sleep(0.01)