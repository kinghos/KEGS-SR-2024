from sr.robot3 import *
robot = Robot()

mb = robot.motor_board.motors

def brake():
    mb[0].power = 0
    mb[1].power = 0

print("Moving forwards")
mb.motors[0].power = 0.4
mb.motors[1].power = 0.4

robot.sleep(5)
print("Braking")
brake()
robot.sleep(1)

print("Moving backwards")
mb.motors[0].power = -0.4
mb.motors[1].power = -0.4

robot.sleep(5)
print("Braking")
brake()
robot.sleep(1)
print("Turning")
mb.motors[0].power = 0.4
mb.motors[1].power = -0.4

robot.sleep(5)


# Useful to test motor current (not needed for challenges) but will probably need later with the actual robot.
print("Motor currents: ", mb.motors[0].current, mb.motors[1].current)
