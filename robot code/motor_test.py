from sr.robot3 import *
robot = Robot()

mb = robot.motor_board.motors

def brake():
    mb[0].power = 0
    mb[1].power = 0

print("Moving forwards")
mb[0].power = 0.4
mb[1].power = 0.4

robot.sleep(5)
print("Braking")
brake()
robot.sleep(1)

print("Moving backwards")
mb[0].power = -0.4
mb[1].power = -0.4

robot.sleep(5)
print("Braking")
brake()
robot.sleep(1)
print("Turning")
mb[0].power = 0.4
mb[1].power = -0.4

robot.sleep(5)


# Useful to test motor current (not needed for challenges) but will probably need later with the actual robot.
print("Motor currents: ", mb[0].current, mb[1].current)
