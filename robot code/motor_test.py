from sr.robot3 import *
robot = Robot()

mb = robot.motor_board.motors

def brake():
    mb[0].power = 0
    mb[1].power = 0

print("Moving forwards")
mb[0].power = 0.4
mb[1].power = 0.4

while True:
    pass
