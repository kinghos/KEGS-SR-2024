from sr.robot3 import *

robot = Robot()

idkey = {
    '150': 'j',
    '151': 'x',
    '152': 's',
    '153': 'z',
    '154': 'b',
    '155': 'w',
    '156': 'm',
    '157': 'f',
    '158': 'c',
    '159': 'h',
    '160': 'k',
    '161': 'q',
    '162': 't',
    '163': 'l',
    '164': 'p',
    '165': 'u',
    '166': 'y',
    '167': 'v',
    '168': 'i',
    '169': 'a',
    '170': 'o',
    '171': 'g',
    '172': 'r',
    '173': 'v',
    '174': 'e',
    '175': 'n'

}




def look_for_any_marker():
    # returns id of first marker it sees
    markers = robot.camera.see()
    if len(markers) > 0:
        print("Found a marker!")
        return markers[0].id
    return -1

# Main code, tries to face a marker
# marker = None

code = ()

# added colon
while True:
    marker = look_for_any_marker()
    if marker != -1:
        print(marker)
        print(idkey[str(marker)])
        code.add(idkey[str(marker)])
        
        # if idkey[str(marker)] != code[-1] or code == []:
        #     code.append(idkey[str(marker)])
        print(code)




