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
robot.sleep(0.3)

print('turning')

while True:
    markers = robot.camera.see()
    angle = markers[0].position.horizontal_angle
    print(angle)
    if angle < 0.1 and angle > -0.1:
        print(1)
        break
    robot.motor_board.motors[0].power = 0.035
    robot.motor_board.motors[1].power = -0.035
    robot.sleep(0.2)

robot.motor_board.motors[0].power = 0
robot.motor_board.motors[1].power = 0
print("Complete")
