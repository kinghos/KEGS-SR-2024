from sr.robot3 import *

robot = Robot()
mtrs = robot.motor_board.motors
duino = robot.arduino
duino.pins[2].mode = INPUT

mtrs[0].power = -0.3
mtrs[1].power = -0.3

while not duino.pins[2].digital_read():
    robot.sleep(0.1)
    
mtrs[0].power = 0
mtrs[1].power = 0