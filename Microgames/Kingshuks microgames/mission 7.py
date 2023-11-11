from sr.robot3 import *

robot = Robot()
duino = robot.arduino
duino.pins[4].mode = OUTPUT
duino.pins[3].mode = OUTPUT
duino.pins[A4].mode = INPUT
reading = robot.arduino.pins[A5].analog_read()
print(f"Rear ultrasound distance value: {reading}")
print(f"Front ultrasound reading: {duino.pins[A4].analog_read()}")

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

duino.pins[4].digital_write(True)

while True:
    markers = robot.camera.see()
    print(f"Front ultrasound reading: {duino.pins[A4].analog_read()}")
    angle = markers[0].position.horizontal_angle
    print(angle)
    if angle < 0.1 and angle > -0.1:
        print(1)
        break
    robot.motor_board.motors[0].power = 0.035
    robot.motor_board.motors[1].power = -0.035
    robot.sleep(0.2)

robot.motor_board.motors[0].power = 0.4
robot.motor_board.motors[1].power = 0.4
robot.sleep(2.8)
robot.motor_board.motors[0].power = 0
robot.motor_board.motors[1].power = 0

duino.pins[4].digital_write(False)

if duino.pins[A4].analog_read() > 4:
    duino.pins[3].digital_write(True)
robot.servo_board.servos[0].position = 1
robot.servo_board.servos[1].position = 1
robot.servo_board.servos[2].position = 1
print("Complete")
duino.pins[3].digital_write(True)
