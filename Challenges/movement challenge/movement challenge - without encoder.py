from sr.robot3 import *
robot = Robot()
mts = robot.motor_board.motors

def move():
    mts[0].power = 1
    mts[1].power = 1

def brake():
    mts[0].power = 0
    mts[1].power = 0

def turn():
    mts[0].power = -1
    mts[1].power = 1

while True:
    move()
    robot.sleep(7)
    brake()
    robot.sleep(0.1)

    turn()
    robot.sleep(2)

    brake()
    robot.sleep(0.1)
    move()
    robot.sleep(10)
    brake()
    robot.sleep(0.1)



    