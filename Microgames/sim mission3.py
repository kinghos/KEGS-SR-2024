from sr.robot3 import *

robot = Robot()


print('moving .5 power')
robot.motor_board.motors[0].power = 0.4
robot.motor_board.motors[1].power = 0.4
# sleep for 2 second
print('sleep 0.5s')
robot.sleep(0.5)

print('stop')
robot.motor_board.motors[0].power = 0
robot.motor_board.motors[1].power = 0


#roughly 20 degrees, once we get to image orientation, we'll use a markers yaw to determine how far we have come
print('turning')
robot.motor_board.motors[0].power = 0.1
robot.motor_board.motors[1].power = -0.1
robot.sleep(0.5)
print('stop')
robot.motor_board.motors[0].power = 0
robot.motor_board.motors[1].power = 0