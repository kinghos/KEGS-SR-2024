# KEGS SR 2024

Project code for the Student Robotics 2024 competition.

Developed by @kinghos, @AreSeven73 and @umar-9

## Firmware

The current firmware file is singleEncoder.ino, and can be loaded onto the Arduino Uno by serial from Arduino IDE. It returns to the Pi the current encoder count. This can be accessed by calling:

```py
robot.arduino.command("e")
```

in robot.py.

## Robot code
The current robot code can be found under `robot code/Final robot code/final code.py`. This must be put into the root directory of the USB to run on start.

The most recent version is "Cleaned up final robot code.py" <br> Previous versions can be found under the Backups folder.