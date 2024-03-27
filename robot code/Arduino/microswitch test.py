from sr.robot3 import *

robot = Robot()
uno = robot.arduino

while True:
    sensorInfo = uno.command("e")
    if sensorInfo:
        print(sensorInfo)
    robot.sleep(0.1)
