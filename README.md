# KEGS SR 2024

Project code for the Student Robotics 2024 competition.

## Firmware

The current firmware file is encoderFirmware.ino, and can be loaded onto the Arduino Uno by serial from Arduino IDE. It returns to the Pi the current encoder count. This can be accessed by calling:

```py
robot.arduino.command("e")
```

in robot.py.

## Robot code
The current robot code can be found under `robot code/Final robot code/robot.py`. This must be put into the root directory of the USB to run on start.
