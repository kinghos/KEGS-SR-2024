from sr.robot3 import *

robot = Robot()
reading = robot.arduino.pins[A5].analog_read()
print(f"Rear ultrasound distance value: {reading}")


robot.motor_board.motors[0].power = 0.4
robot.motor_board.motors[1].power = 0.4

robot.sleep(0.5)

robot.motor_board.motors[0].power = 0
robot.motor_board.motors[1].power = 0

print('turning')
robot.motor_board.motors[0].power = 0.1
robot.motor_board.motors[1].power = -0.1
robot.sleep(0.5)
print('stop')
robot.motor_board.motors[0].power = 0
robot.motor_board.motors[1].power = 0