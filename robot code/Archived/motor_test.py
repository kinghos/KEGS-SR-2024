from sr.robot3 import *
robot = Robot()

drive_board = robot.motor_boards["SR0UK1L"].motors
mech_board = robot.motor_boards["SR0KJ15"].motors

def brake():
    drive_board[0].power = 0
    drive_board[1].power = 0

print("Moving forwards")
drive_board[0].power = 0.4
drive_board[1].power = 0.4
robot.sleep(2)
print("braking")
brake()
robot.sleep(1)
print("mechanism power")
mech_board[0].power = 1
mech_board[1].power = 1
robot.sleep(2)
mech_board[0].power = 0
mech_board[1].power = 0

while True:
    pass
