from sr.robot3 import *
import math

robot = Robot()
mts = robot.motor_board.motors
pins = robot.arduino.pins


ENCODER_CYCLE = (2 * math.pi) / (2 * 374)
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
    on_short_side = True

    while True:
        turning = False

        # With 80mm wheels, there are 4 full cycles in 1000mm, and 6 full cycles in 1500mm
        cycles = 0
        counts = 0

        # Reads initial encoder position as a binary string
        prev_seq = str(int(pins[2].digital_read())) + str(int(pins[3].digital_read()))
        seq_pos = sequence.index(prev_seq)
        rad_rotated = 0

        while not turning:
            mts[0].power = 0.1
            mts[1].power = 0.1

            encoderA = str(int(pins[2].digital_read()))
            encoderB = str(int(pins[3].digital_read()))
            bin_str = encoderA + encoderB
            str_idx = sequence.index(bin_str)
            #print(f"BINSTR: {bin_str}\t IDX: {str_idx}")
            #print(f"Current encoder: {bin_str}\n")#Prev encoder: {prev_seq}")



            # Checks to see if the new binary string read follows the previous reading in the sequence, going clockwise
            if str_idx == -1:
                print("String not found in sequence!!!!")
            else:
                counts += abs(str_idx - seq_pos)
                print(counts)
                rad_rotated += ENCODER_CYCLE * abs(str_idx - seq_pos)
                print(f"Rad rotated: {rad_rotated}")
                seq_pos = str_idx
                prev_seq = bin_str

            if rad_rotated >= 2 * math.pi:
                cycles += 1
                rad_rotated = 0
                print(f'1{cycles} cycles')
                #print(f'{rad_rotated} rad rotated')

            if cycles == 4 and on_short_side:
                on_short_side = False
                turning = True
            elif cycles == 6 and not on_short_side:
                on_short_side = True
                turning = True

            #robot.sleep(0.1) # - why is this here
        print("LOOP EXITED-----------------------------------------------------------------------------")

        mts[0].power = 0
        mts[1].power = 0
        robot.sleep(0.2)

        # Robot turns left (?)
        # Needs adjustment
        mts[0].power = -0.2
        mts[1].power = 0.2
        robot.sleep(3)


encoderLoop()



