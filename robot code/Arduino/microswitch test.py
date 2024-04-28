from sr.robot3 import *

robot = Robot()
uno = robot.arduino

def getSensorData():
    while True:
        robot.sleep(0.05)
        sensorInfo = uno.command("e")
        if sensorInfo:
            print(sensorInfo)
            return(sensorInfo.split(","))
        
while True:
    getSensorData()
    robot.sleep(2)