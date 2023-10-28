import time
from sr.robot3 import Robot
robot = Robot()
while True:
    robot.kch.leds[LED_A].colour = Colour.RED
    robot.kch.leds[LED_B].colour = Colour.RED
    robot.kch.leds[LED_C].colour = Colour.RED
    time.sleep(1.0)
    robot.kch.leds[LED_A].colour = Colour.GREEN
    robot.kch.leds[LED_B].colour = Colour.GREEN
    robot.kch.leds[LED_C].colour = Colour.GREEN
    time.sleep(1.0)
    robot.kch.leds[LED_A].colour = Colour.BLUE
    robot.kch.leds[LED_B].colour = Colour.BLUE
    robot.kch.leds[LED_C].colour = Colour.BLUE
    time.sleep(1.0)


