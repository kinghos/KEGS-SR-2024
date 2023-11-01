from sr.robot3 import *
robot = Robot()


# MISSION 3
robot.motor_board.motors[0].power = robot.motor_board.motors[1].power = 0.4
robot.sleep(0.5)
robot.motor_board.motors[1].power = 0
robot.motor_board.motors[0].power = 1
robot.sleep(0.1)
robot.motor_board.motors[0].power = robot.motor_board.motors[1].power = 0
robot.sleep(1)
print("MISSION 3 completed")

# MISSION 4
markers = robot.camera.see()
robot.motor_board.motors[1].power = 0
robot.motor_board.motors[0].power = 1

robot.arduino.pins[4].mode = robot.arduino.pins[3].mode = OUTPUT
robot.arduino.pins[4].digital_write(True)

while markers[0].position.horizontal_angle > 0.035:
    markers = robot.camera.see()
robot.motor_board.motors[1].power = 0.4
robot.motor_board.motors[0].power = 0.4
robot.sleep(1)
print("MISSION 4 completed")

# MISSION 5
robot.sleep(2)
robot.motor_board.motors[0].power = robot.motor_board.motors[1].power = 0
robot.servo_board.servos[0].position = robot.servo_board.servos[1].position = 0.7
robot.sleep(0.5)
robot.servo_board.servos[2].position = 1
robot.sleep(1)
print("MISSION 5 completed")

# MISSION 6
robot.arduino.pins[4].digital_write(False)
robot.arduino.pins[3].digital_write(True)