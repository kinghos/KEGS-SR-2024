from sr.robot3 import *
robot = Robot()

while True:
    markers = robot.camera.see()
    print("I can see", len(markers), "markers:")

    for marker in markers:
        print("Marker #{0} is {1} metres away".format(
            marker.id,
            marker.position.distance / 1000,
        ))