from sr.robot3 import *
import math

robot = Robot()
mts = robot.motor_board.motors
pins = robot.arduino.pins

ENCODER_CYCLE = (2 * math.pi) / 11
pins[2].mode = INPUT
pins[3].mode = INPUT

sequence = [
    "01",
    "00",
    "10",
    "11"
]

on_short_side = True

while True:
    turning = False

    # With 80mm wheels, there are 4 full cycles in 1000mm, and 6 full cycles in 1500mm
    cycles = 0


    # Reads initial encoder position as a binary string
    prev_seq = str(int(pins[2].digital_read())) + str(int(pins[3].digital_read()))
    seq_pos = sequence.find(prev_seq)
    degrees_rotated = 0

    while not turning:
        mts[0].power = 0.7
        mts[1].power = 0.7

        encoderA = str(int(pins[2].digital_read()))
        encoderB = str(int(pins[3].digital_read()))
        bin_str = encoderA + encoderB
        str_idx = sequence.find(bin_str)

        # Checks to see if the new binary string read follows the previous reading in the sequence, going clockwise
        if (prev_seq != bin_str) and (str_idx == (seq_pos + 1) % 4):
            degrees_rotated += ENCODER_CYCLE 
            seq_pos += 1
            seq_pos = seq_pos % 4
            prev_seq = bin_str
        
        if degrees_rotated == 2 * math.pi:
            cycles += 1
        
        if cycles == 4 and on_short_side:
            on_short_side = False
            turning = True
        elif cycles == 6 and not on_short_side:
            on_short_side = True
            turning = True
    
    mts[0].power = 0
    mts[1].power = 0
    robot.sleep(0.2)

    # Robot turns left (?)
    # Needs adjustment
    mts[0].power = -0.2
    mts[1].power = 0.2
    robot.sleep(3)
    

        



