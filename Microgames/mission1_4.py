from sr.robot3 import *
robot = Robot()

while True:
    robot.kch.leds[LED_A] = robot.kch.leds[LED_B] = robot.kch.leds[LED_C] = Colour.RED
    robot.sleep()
    robot.kch.leds[LED_A] = robot.kch.leds[LED_B] = robot.kch.leds[LED_C] = Colour.GREEN
    robot.sleep()
    robot.kch.leds[LED_A] = robot.kch.leds[LED_B] = robot.kch.leds[LED_C] = Colour.BLUE