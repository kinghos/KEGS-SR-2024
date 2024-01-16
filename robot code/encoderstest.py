from sr.robot3 import *
import math

robot = Robot()
mts = robot.motor_board.motors
pins = robot.arduino.pins


# ENCODER_CYCLE = (0.5*math.pi) / (34) - closest one yet (around 2 cycles out at 20 cycles)
# ENCODER_CYCLE = (0.25*math.pi) / (2*11) # - seems to be pretty much bang on
# ENCODER_CYCLE = (10*math.pi) / (2*374) # - drifts around 2-3 cycles out (too low) at 30 cycles
ENCODER_CYCLE = (math.pi) / (2*34)

pins[2].mode = INPUT
pins[3].mode = INPUT

# sequence: AB (A is MSB, B is LSB)
sequence = [
    "01",
    "00",
    "10",
    "11"
]

def encoderLoop():
    mts[0].power = 0.2
    mts[1].power = 0.2
    encoderA = str(int(pins[2].digital_read()))
    encoderB = str(int(pins[3].digital_read()))
    prev_seq = encoderA + encoderB
    seq_pos = sequence.index(prev_seq)
    cycles = 0
    rad_rotated = 0
    while True:
        encoderA = str(int(pins[2].digital_read()))
        encoderB = str(int(pins[3].digital_read()))
        bin_str = encoderA + encoderB
        str_idx = sequence.index(bin_str)

        rad_rotated += ENCODER_CYCLE * abs(str_idx - seq_pos)
        #print(rad_rotated)
        if rad_rotated >= 2*math.pi:
            cycles += 1
            print(f"---------------------------------------------CYCLE {cycles}---------------------------------------------")
            rad_rotated = 0
    #robot.sleep(0.1)


encoderLoop()
