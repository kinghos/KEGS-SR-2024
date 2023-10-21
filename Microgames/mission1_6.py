from sr.robot3 import *
robot = Robot()


conversion_table = {
    150: "J",
    151: "X",
    152: "S",
    153: "Z",
    154: "B",
    155: "W",
    156: "M",
    157: "F", 
    158: "C", 
    159: "H",
    160: "K",
    161: "Q",
    162: "T",
    163: "L",
    164: "P",
    165: "U",
    166: "Y",
    167: "V",
    168: "I",
    169: "A",
    170: "O",
    171: "G",
    172: "R",
    173: "V",
    174: "E",
    175: "N",
}


while True:
    markers = robot.camera.see()

    for marker in markers.sort(key=marker.pixel_centre.x):
        print(f"{conversion_table[marker.id]}", end="")

    print("\n")