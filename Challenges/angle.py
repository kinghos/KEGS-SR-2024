"""Autonomously demonstrate, using the LEDs on the Brain Board, awareness of its position relative to an arena wall marker.
Facing the wall at a point between 1 and 3 metres out from the wall and directly in front of the middle of the marker:

turn on the spot illuminating LEDs to indicate the orientation of the robot:
    LED A in yellow when more than 15° left from square on,
    LED B in yellow in the middle (30° arc) and
    LED C in yellow when more than 15 right from square on.

move left and right illuminating LEDs to indicate the position of the robot relative to a line through the marker and orthogonal to the wall:
    LED A in blue when more than 200mm left of the line
    LED B in yellow within 200mm of the line
    LED C in blue when more than 200mm right of the line

The robot may move autonomously or may be moved manually to complete this challenge.
Note: if moving the robot manually then the Arduino, Motor and Servo Boards must be disconnected
from the Power Board as well as any mechanical components secured for the duration of the demonstration."""

import math
from sr.robot3 import *
robot = Robot()

wallmarker = 0

#find a desired target marker and return its information
def look(targetid):
    markers = robot.camera.see()
    for marker in markers:
        if marker.id == targetid:
            return marker
    print(f'couldnt find {targetid}')
    return None
cycle = 0
while True:
    cycle += 1

    robot.camera.save(robot.usbkey / f"/vision camera/vision_challenge{cycle}.jpg")
    arr = robot.camera.capture()
    #wanted to put it into
    #D:\vision camera

    #camera.see for target marker and return info
    current = look(wallmarker)
    print(current)

    if current:
        print(f'angle: {current.position.horizontal_angle}')
        #if angle then make x led yellow
        if current.position.horizontal_angle > (15/360)*2*math.pi:
            robot.kch.leds[LED_A].colour = Colour.YELLOW
            print('angle left')
        elif current.position.horizontal_angle < -(15/360)*2*math.pi:
            robot.kch.leds[LED_C].colour = Colour.YELLOW
            print('angle right')
        else:
            robot.kch.leds[LED_B].colour = Colour.YELLOW
            print('angle mid')

        robot.sleep(0.1)



